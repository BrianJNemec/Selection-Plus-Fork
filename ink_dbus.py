import sys

from time import sleep

import gi
gi.require_version("Gio", "2.0")
from gi.repository import Gio, GLib

path_id_list = sys.argv[4]
path_id_list = path_id_list_string = path_id_list[1:-1]
path_id_list = path_id_list.split(',')
path_id_list_string = ','.join(path_id_list)
path_id_list_string = f'{path_id_list_string}'

dbus_delay_float = float(sys.argv[5])
clear_selection = sys.argv[6]

# with open("/home/name/test.txt", mode='w', encoding='utf-8') as file:
#     string = 'hello'
#     file.write(path_id_list_string)
#     # file.write(string)
#     file.close()
#
# sys.exit()

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

if clear_selection == 'true':

    InkDbus.ink_dbus_action(None, 'application', 'select-clear', None, None)

InkDbus.ink_dbus_action(None, 'application', 'select-by-id', path_id_list_string, None)

sys.exit()