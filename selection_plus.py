#!/usr/bin/env python
# coding=utf-8
#
# Copyright (C) [2022] [Matt Cottam], [mpcottam@raincloud.co.uk]
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

##############################################################################
# Selection Plus - a dbus based inkscape selection passback extension
# An Inkscape 1.2.1+ extension
##############################################################################

import subprocess

import sys, os

import inkex

def get_attributes(self):
    """ Returns a string containing all object attributes
         - One attribute per line
    """
    attribute_string = 'test'
    for att in dir(self):
        try:
            attribute = (att, getattr(self, att))
            attribute_string = attribute_string + str(attribute) + '\n'
        except:
            None
    return attribute_string


# Platform Check
################
def os_check(self):
    """
    Check which OS we are using
    :return: OS Name ( windows, linux, macos )
    """
    from sys import platform

    if 'linux' in platform.lower():
        return 'linux'
    elif 'darwin' in platform.lower():
        return 'macos'
    elif 'win' in platform.lower():
        return 'windows'


# Functions to silence stderr and stdout
# Close output pipeline ( See notes at top of script )
# If they are not silenced, any messages prevent the selection passback
def set_stdout(self, state):
    import sys, os
    if state == 'off':
        sys.stdout = open(os.devnull, 'w')
    else:
        sys.stdout.close()
        sys.stdout = sys.__stdout__


def set_stderr(self, state):
    import sys, os
    if state == 'off':
        sys.stderr = open(os.devnull, 'w')
    else:
        sys.stderr.close()
        sys.stderr = sys.__stderr__


set_stdout(None, 'off')
set_stderr(None, 'off')


class SelectionPassback(inkex.EffectExtension):

    def add_arguments(self, pars):

        pars.add_argument("--selection_plus_notebook", type=str, dest="selection_plus_notebook", default=0)

        pars.add_argument("--selection_type_radio", type=str, dest="selection_type_radio", default='path')

        pars.add_argument("--dbus_delay_float", type=float, dest="dbus_delay_float", default=0.5)

        pars.add_argument("--clear_selection_cb", type=str, dest="clear_selection_cb", default='true')

    def effect(self):

        dbus_delay = str(self.options.dbus_delay_float)

        clear_selection = self.options.clear_selection_cb

        selection_string = f'//svg:{self.options.selection_type_radio}'

        paths = self.svg.xpath(selection_string)

        path_id_list = []

        for path in paths:
            path_id_list.append(path.get_id())

        path_id_list_string = f"\'{','.join(path_id_list)}\'"

        if os_check(self) == 'windows':
            DETACHED_PROCESS = 0x08000000
            subprocess.Popen(['c:/program files/inkscape/bin/python.exe', 'ink_dbus.py',  'application', 'None', 'None', path_id_list_string, dbus_delay, clear_selection], creationflags=DETACHED_PROCESS)
        else:
            subprocess.Popen(['python3', 'ink_dbus.py', 'application', 'None', 'None', path_id_list_string, dbus_delay, clear_selection],
                         preexec_fn=os.setpgrp, stdout=open('/dev/null', 'w'),
                         stderr=open('/dev/null', 'w'), )

        sys.exit()


if __name__ == '__main__':
    SelectionPassback().run()
