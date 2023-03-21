import sys

from time import sleep

import gi
import inkex

gi.require_version("Gio", "2.0")
from gi.repository import Gio, GLib

# Needed to write debug info - as not possible to see subprocess
# stdout / stderr in Inkscape
def write_debug_file(data):
    with open("/home/name/test.txt", mode='a', encoding='utf-8') as file:
        file.write(str(data))
        file.close()

def selection_arg_to_list(selection_arg):

    arg_string = selection_arg[1:-1]
    id_list = arg_string.split(',')
    id_list_string = ','.join(id_list)
    id_list_string = f'{id_list_string}'
    return id_list, id_list_string

# Get the selection criteria
path_id_args = sys.argv[4]
path_id_list, dummy_string = selection_arg_to_list(path_id_args)

# Delay (mainly for windows systems)
dbus_delay_float = float(sys.argv[5])

# Should we Clear current selection, add to it, or subtract from it ?
selection_mode = sys.argv[6]

# The currently selected objects in the document
current_selection_id_list_string = sys.argv[7]
current_selection_id_list, dummy_string = selection_arg_to_list(current_selection_id_list_string)

class InkDbus:

    def ink_dbus_action(self, path, action, param, id_list):

        if path == 'document':
            action_path = InkDbus.applicationGroup
        elif path == 'application':
            action_path = InkDbus.applicationGroup
        elif path == 'window':
            action_path = InkDbus.windowGroup

        if param != None:

            param_string = GLib.Variant.new_string(param)

            action_path.activate_action(action, param_string)
        else:
            action_path.activate_action(action)


    def start_bus(self):

        try:
            bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)

        except BaseException:
            # print("No DBus bus")
            exit()

        # print ("Got DBus bus")

        proxy = Gio.DBusProxy.new_sync(bus, Gio.DBusProxyFlags.NONE, None,
                                       'org.freedesktop.DBus',
                                       '/org/freedesktop/DBus',
                                       'org.freedesktop.DBus', None)

        names_list = proxy.call_sync('ListNames', None, Gio.DBusCallFlags.NO_AUTO_START, 500, None)

        # names_list is a GVariant, must unpack

        names = names_list.unpack()[0]

        # Look for Inkscape; names is a tuple.

        for name in names:
            if ('org.inkscape.Inkscape' in name):
                # print ("Found: " + name)
                break

        # print ("Name: " + name)

        appGroupName = "/org/inkscape/Inkscape"
        winGroupName = appGroupName + "/window/1"
        docGroupName = appGroupName + "/document/1"

        InkDbus.applicationGroup = Gio.DBusActionGroup.get(bus, name, appGroupName)
        InkDbus.windowGroup = Gio.DBusActionGroup.get(bus, name, winGroupName)
        InkDbus.documentGroup = Gio.DBusActionGroup.get(bus, name, docGroupName)

## Start of selection code

InkDbus.start_bus(None)

sleep(dbus_delay_float)

if selection_mode == 'clear':

    InkDbus.ink_dbus_action(None, 'application', 'select-clear', None, None)

elif selection_mode == 'add':

    path_id_list = list(set(path_id_list + current_selection_id_list))

elif selection_mode == 'subtract':

    path_id_list = [x for x in current_selection_id_list if x not in path_id_list]

path_id_list_string = f"{','.join(path_id_list)}"

InkDbus.ink_dbus_action(None, 'application', 'select-by-id', path_id_list_string, None)

sys.exit()