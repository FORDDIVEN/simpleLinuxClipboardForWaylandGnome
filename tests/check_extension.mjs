// Structural lifecycle test with GNOME objects mocked; not a GNOME runtime test.
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
let source = fs.readFileSync('gnome-extension/extension.js', 'utf8')
    .replace(/^import .*;\n/gm, '').replace('export default class', 'class');
source += '\nglobalThis.Bridge = ClipboardBridge;';
const bindings = new Map();
let devices = 0;
let strokes = 0;
const target = {activate() { context.global.display.focus_window = target; }};
const context = vm.createContext({
    console,
    Extension: class { getSettings() { return {set_strv() {}}; } },
    Gio: {
        DBus: {session: {call() {}}}, BusNameOwnerFlags: {NONE: 0},
        BusNameWatcherFlags: {NONE: 0}, DBusCallFlags: {NO_AUTO_START: 0},
        DBusExportedObject: {wrapJSObject() {return {export() {}, unexport() {}};}},
        bus_own_name_on_connection() {return 1;}, bus_watch_name_on_connection() {return 2;},
        bus_unwatch_name() {}, bus_unown_name() {},
    },
    GLib: {Variant: class {}, Bytes: class {}, base64_decode() {return [];}},
    Meta: {KeyBindingFlags: {NONE: 0}, KeyBindingAction: {NONE: 0}},
    Shell: {ActionMode: {NORMAL: 1}},
    Clutter: {InputDeviceType: {KEYBOARD_DEVICE: 1}, KeyState: {PRESSED: 1, RELEASED: 0},
        ModifierType: {SUPER_MASK: 1, CONTROL_MASK: 2, MOD1_MASK: 4}, KEY_Control_L: 10, KEY_v: 11},
    St: {Clipboard: {get_default() {return {set_content() {}};}}, ClipboardType: {CLIPBOARD: 1}},
    Main: {wm: {removeKeybinding(key) {bindings.delete(key);}, addKeybinding(key, ...args) {bindings.set(key, args.at(-1)); return 1;}}},
    global: {
        stage: {context: {get_backend() {return {get_default_seat() {return {create_virtual_device() {
            devices++; return {notify_keyval() {strokes++;}, run_dispose() {}};
        }};}};}}},
        display: {get_selection() {return {connect() {return 1;}, disconnect() {}};}, connect() {return 1;}, disconnect() {}},
        window_manager: {connect() {return 1;}, disconnect() {}},
        get_window_actors() {return [{meta_window: target}];}, get_current_time() {return 1;}, get_pointer() {return [0, 0, 0];},
    },
});
vm.runInContext(source, context);
const bridge = new context.Bridge();
bridge.enable();
assert.equal(devices, 0, 'shortcut startup must not require a virtual keyboard');
bridge.Request(JSON.stringify({action: 'configure', enabled: true, shortcut: 'Meta+V'}));
assert(bindings.has('winv-toggle'));
bridge._target = target;
bridge._later = (_delay, callback) => callback();
bridge.Request(JSON.stringify({action: 'paste', mime: 'text/plain', data: ''}));
assert.equal(devices, 1);
assert.equal(strokes, 4);
bridge.disable();
assert.equal(bindings.size, 0);
console.log('Extension mocked lifecycle: enable, configure, lazy keyboard, paste, disable OK');
