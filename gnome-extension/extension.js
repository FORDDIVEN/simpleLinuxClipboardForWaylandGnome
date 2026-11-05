import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import Meta from 'gi://Meta';
import Clutter from 'gi://Clutter';
import Shell from 'gi://Shell';
import St from 'gi://St';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

const APP = 'io.github.winvclipboard.Wayland';
const PATH = '/io/github/winvclipboard/Wayland';
const XML = `<node><interface name="${APP}.Shell"><method name="Request"><arg type="s" direction="in"/></method></interface></node>`;
const LIMIT = 16 * 1024 * 1024;

export default class ClipboardBridge extends Extension {
    enable() {
        this._active = true;
        this._sources = new Set();
        this._settings = this.getSettings();
        this._clipboard = St.Clipboard.get_default();
        this._selection = global.display.get_selection();
        this._keyboard = null; // Create lazily: paste support must not prevent shortcut startup.
        this._export = Gio.DBusExportedObject.wrapJSObject(XML, this);
        this._export.export(Gio.DBus.session, PATH);
        this._owner = Gio.bus_own_name_on_connection(Gio.DBus.session, `${APP}.Shell`, Gio.BusNameOwnerFlags.NONE,
            () => this._call('Ready', null), null);
        this._watch = Gio.bus_watch_name_on_connection(Gio.DBus.session, APP, Gio.BusNameWatcherFlags.NONE,
            () => { this._call('Ready', null); this._capture(); }, () => this._bind(false));
        this._selectionId = this._selection.connect('owner-changed', (_s, type) => {
            if (type === Meta.SelectionType.SELECTION_CLIPBOARD) this._capture();
        });
        this._mapId = global.window_manager.connect('map', (_wm, actor) => {
            const win = actor.meta_window;
            if (this._isApp(win)) this._place(win);
        });
        this._grabId = global.display.connect('grab-op-end', (_d, win) => {
            if (!this._isApp(win)) return;
            const rect = win.get_frame_rect();
            this._position = [rect.x, rect.y];
            this._call('Position', new GLib.Variant('(ii)', this._position));
        });
        this._bind(false);
    }

    _call(method, params) {
        Gio.DBus.session.call(APP, PATH, APP, method, params, null,
            Gio.DBusCallFlags.NO_AUTO_START, 1000, null, (bus, result) => {
                try { bus.call_finish(result); } catch (e) { console.debug(`WinV: ${e.message}`); }
            });
    }

    _isApp(win) { return win && win.get_wm_class() === APP && win.get_title() === 'Clipboard'; }

    _bind(enabled) {
        Main.wm.removeKeybinding('winv-toggle');
        if (enabled) {
            const action = Main.wm.addKeybinding('winv-toggle', this._settings, Meta.KeyBindingFlags.NONE,
            Shell.ActionMode.NORMAL, () => {
                const focus = global.display.focus_window;
                if (!this._isApp(focus)) this._target = focus;
                this._call('Toggle', null);
            });
            if (action === Meta.KeyBindingAction.NONE)
                console.error('WinV: no se pudo registrar el atajo; comprueba conflictos en GNOME');
        }
    }

    _later(delay, callback) {
        const id = GLib.timeout_add(GLib.PRIORITY_DEFAULT, delay, () => {
            this._sources.delete(id);
            if (this._active) callback();
            return GLib.SOURCE_REMOVE;
        });
        this._sources.add(id);
    }

    _place(win) {
        if (!this._target || this._isApp(this._target)) {
            const previous = global.display.get_tab_list(Meta.TabList.NORMAL_ALL, null).find(w => !this._isApp(w));
            this._target = previous;
        }
        if (this._position) {
            const area = Main.layoutManager.getWorkAreaForMonitor(win.get_monitor());
            const rect = win.get_frame_rect();
            const x = Math.max(area.x, Math.min(this._position[0], area.x + area.width - rect.width));
            const y = Math.max(area.y, Math.min(this._position[1], area.y + area.height - rect.height));
            win.move_frame(true, x, y);
        }
        win.activate(global.get_current_time());
    }

    Request(payload) {
        const request = JSON.parse(payload);
        if (request.action === 'configure') {
            this._position = request.position;
            const parts = request.shortcut.split('+');
            const key = parts.pop();
            const mods = parts.map(p => `<${p === 'Meta' ? 'Super' : p}>`).join('');
            this._settings.set_strv('winv-toggle', [mods + key]);
            this._bind(request.enabled);
        } else if (request.action === 'show') {
            const focus = global.display.focus_window;
            if (focus && !this._isApp(focus)) this._target = focus;
            const win = global.get_window_actors().map(a => a.meta_window).find(w => this._isApp(w));
            if (win) this._place(win);
        } else if (request.action === 'paste') {
            if (request.data.length > LIMIT * 4 / 3 + 4) throw new Error('Clipboard limit exceeded');
            const bytes = new GLib.Bytes(GLib.base64_decode(request.data));
            this._clipboard.set_content(St.ClipboardType.CLIPBOARD,
                request.mime === 'text/plain' ? 'text/plain;charset=utf-8' : request.mime, bytes);
            const target = this._target;
            if (!target || !global.get_window_actors().some(a => a.meta_window === target)) return;
            target.activate(global.get_current_time());
            this._later(180, () => {
                if (global.display.focus_window !== target) return;
                // Wait until the opening shortcut's modifiers have been released.
                const [, , mods] = global.get_pointer();
                if (mods & (Clutter.ModifierType.SUPER_MASK | Clutter.ModifierType.CONTROL_MASK | Clutter.ModifierType.MOD1_MASK)) return;
                this._keyboard ??= global.stage.context.get_backend().get_default_seat()
                    .create_virtual_device(Clutter.InputDeviceType.KEYBOARD_DEVICE);
                const keys = [Clutter.KEY_Control_L, Clutter.KEY_v];
                for (const key of keys) this._keyboard.notify_keyval(0, key, Clutter.KeyState.PRESSED);
                for (const key of keys.reverse()) this._keyboard.notify_keyval(0, key, Clutter.KeyState.RELEASED);
            });
        }
    }

    _capture() {
        const generation = this._generation = (this._generation ?? 0) + 1;
        const types = this._selection.get_mimetypes(Meta.SelectionType.SELECTION_CLIPBOARD);
        const mime = ['image/png', 'image/jpeg', 'image/webp', 'text/plain;charset=utf-8', 'text/plain'].find(t => types.includes(t));
        if (!mime) return;
        // Bound transfers in Mutter before allocating or sending D-Bus payloads.
        const stream = Gio.MemoryOutputStream.new_resizable();
        this._selection.transfer_async(Meta.SelectionType.SELECTION_CLIPBOARD, mime, LIMIT + 1,
            stream, null, (selection, result) => {
                try {
                    selection.transfer_finish(result);
                    stream.close(null);
                    if (!this._active || generation !== this._generation || stream.get_data_size() > LIMIT) return;
                    const bytes = stream.steal_as_bytes().get_data();
                    this._call('Capture', new GLib.Variant('(ss)', [mime.startsWith('text/') ? 'text/plain' : mime, GLib.base64_encode(bytes)]));
                } catch (e) { console.debug(`WinV capture: ${e.message}`); }
            });
    }

    disable() {
        this._active = false;
        Main.wm.removeKeybinding('winv-toggle');
        for (const id of this._sources) GLib.source_remove(id);
        this._sources.clear();
        this._selection.disconnect(this._selectionId);
        global.window_manager.disconnect(this._mapId);
        global.display.disconnect(this._grabId);
        Gio.bus_unwatch_name(this._watch);
        Gio.bus_unown_name(this._owner);
        this._export.unexport();
        this._keyboard?.run_dispose();
        this._keyboard = null;
        this._target = null;
    }
}
