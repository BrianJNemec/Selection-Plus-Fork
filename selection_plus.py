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

from py.sp_bbox import SpBbox
from py.sp_path import SpPath

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

# import warnings
# warnings.filterwarnings("ignore")

def pass_ids_to_dbus(self, path_id_list_string, dbus_delay, clear_selection):

    if os_check(self) == 'windows':

        py_exe = sys.executable
        if 'pythonw.exe' in py_exe:
            py_exe = py_exe.replace('pythonw.exe', 'python.exe')

        DETACHED_PROCESS = 0x08000000
        subprocess.Popen([py_exe, 'ink_dbus.py',  'application', 'None', 'None', path_id_list_string, dbus_delay, clear_selection], creationflags=DETACHED_PROCESS)
    else:
        subprocess.Popen(['python3', 'ink_dbus.py', 'application', 'None', 'None', path_id_list_string, dbus_delay, clear_selection],
                         preexec_fn=os.setpgrp, stdout=open('/dev/null', 'w'),
                         stderr=open('/dev/null', 'w'), )

###############################################
# Path selection functions
###############################################


###############################################
# End of Path selection functions
###############################################

###############################################
# Bounding Box selection functions
###############################################




###############################################
# End of Bounding Box selection functions
###############################################


class SelectionPassback(inkex.EffectExtension):

    def add_arguments(self, pars):

        pars.add_argument("--selection_plus_notebook", type=str, dest="selection_plus_notebook", default=0)

        pars.add_argument("--selection_type_radio", type=str, dest="selection_type_radio", default='path')

        pars.add_argument("--dbus_delay_float", type=float, dest="dbus_delay_float", default=0.5)

        pars.add_argument("--clear_selection_cb", type=str, dest="clear_selection_cb", default='true')

        # Path Page
        pars.add_argument("--path_type_combo", type=str, dest="path_type_combo", default='absolute')

        pars.add_argument("--node_count_bool", type=inkex.Boolean, dest="node_count_bool", default=True)
        pars.add_argument("--node_count_lower", type=float, dest="node_count_lower", default=16)
        pars.add_argument("--node_count_upper", type=float, dest="node_count_upper", default=16)

        # xpath Page
        pars.add_argument("--xpath_string_radio", type=str, dest="xpath_string_radio", default='1')
        pars.add_argument("--xpath_user_string1", type=str, dest="xpath_user_string1", default='x')
        pars.add_argument("--xpath_user_string2", type=str, dest="xpath_user_string2", default='x')
        pars.add_argument("--xpath_user_string3", type=str, dest="xpath_user_string3", default='x')
        pars.add_argument("--xpath_user_string4", type=str, dest="xpath_user_string4", default='x')
        pars.add_argument("--xpath_user_string5", type=str, dest="xpath_user_string5", default='x')
        pars.add_argument("--xpath_user_string6", type=str, dest="xpath_user_string6", default='x')

        # Bounding Box Page

        pars.add_argument("--bbox_unit_choice_bool", type=inkex.Boolean, dest="bbox_unit_choice_bool", default=False)

        pars.add_argument("--bbox_unit_choice_combo", type=str, dest="bbox_unit_choice_combo", default='px')

        pars.add_argument("--bbox_width_bool", type=inkex.Boolean, dest="bbox_width_bool", default=True)
        pars.add_argument("--bbox_width_lower", type=float, dest="bbox_width_lower", default=16)
        pars.add_argument("--bbox_width_upper", type=float, dest="bbox_width_upper", default=16)

        pars.add_argument("--bbox_height_bool", type=inkex.Boolean, dest="bbox_height_bool", default=True)
        pars.add_argument("--bbox_height_lower", type=float, dest="bbox_height_lower", default=16)
        pars.add_argument("--bbox_height_upper", type=float, dest="bbox_height_upper", default=16)

        pars.add_argument("--bbox_diagonal_bool", type=inkex.Boolean, dest="bbox_diagonal_bool", default=True)
        pars.add_argument("--bbox_diagonal_lower", type=float, dest="bbox_diagonal_lower", default=16)
        pars.add_argument("--bbox_diagonal_upper", type=float, dest="bbox_diagonal_upper", default=16)

        pars.add_argument("--bbox_area_bool", type=inkex.Boolean, dest="bbox_area_bool", default=True)
        pars.add_argument("--bbox_area_lower", type=float, dest="bbox_area_lower", default=16)
        pars.add_argument("--bbox_area_upper", type=float, dest="bbox_area_upper", default=16)

        pars.add_argument("--bbox_ratio_width_height_bool", type=inkex.Boolean, dest="bbox_ratio_width_height_bool", default=True)
        pars.add_argument("--bbox_ratio_width_height_lower", type=float, dest="bbox_ratio_width_height_lower", default=16)
        pars.add_argument("--bbox_ratio_width_height_upper", type=float, dest="bbox_ratio_width_height_upper", default=16)

        pars.add_argument("--bbox_ratio_height_width_bool", type=inkex.Boolean, dest="bbox_ratio_height_width_bool", default=True)
        pars.add_argument("--bbox_ratio_height_width_lower", type=float, dest="bbox_ratio_height_width_lower", default=16)
        pars.add_argument("--bbox_ratio_height_width_upper", type=float, dest="bbox_ratio_height_width_upper", default=16)



    def effect(self):

        id_list = []

        dbus_delay = str(self.options.dbus_delay_float)

        clear_selection = self.options.clear_selection_cb

        if self.options.selection_plus_notebook == 'settings_page':
            selection_string = f'//svg:{self.options.selection_type_radio}'
            try:
                elements = self.svg.xpath(selection_string)
                for element in elements:
                    id_list.append(element.get_id())
            except:
                sys.exit()

        elif self.options.selection_plus_notebook == 'path_page':
            selection_string = f'//svg:path'
            paths = self.svg.xpath(selection_string)
            id_list = SpPath.paths_thres_node_count(self, paths)

        elif self.options.selection_plus_notebook == 'xpath_page':
            selected_xpath_string = 'xpath_user_string' + self.options.xpath_string_radio

            xpath_string = getattr(self.options, selected_xpath_string)
            # selection_string = f'{self.options.xpath_string_input_box}'

            try:
                elements = self.svg.xpath(xpath_string)
                for element in elements:
                    id_list.append(element.get_id())
            except:
                sys.exit()

        elif self.options.selection_plus_notebook == 'bounding_box_page':
            selection_string = '//svg:circle | //svg:ellipse | //svg:line | //svg:tspan | //svg:tspan | //svg:path | //svg:polygon | //svg:polyline | //svg:rect'

            selection_list = self.svg.xpath(selection_string)

            id_list = SpBbox.chain_thres(self, selection_list)



        # Command separated id string ( not a list )
        id_list_string = f"\'{','.join(id_list)}\'"

        # Call selection function
        pass_ids_to_dbus(self, id_list_string, dbus_delay, clear_selection)

        sys.exit()

        # Comment just to trigger merge

if __name__ == '__main__':
    SelectionPassback().run()
