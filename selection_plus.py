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
from py.sp_color import SpColor

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

def pass_ids_to_dbus(self, path_id_list_string, dbus_delay, selection_mode, current_selection_id_list_string):

    if os_check(self) == 'windows':

        py_exe = sys.executable
        if 'pythonw.exe' in py_exe:
            py_exe = py_exe.replace('pythonw.exe', 'python.exe')

        DETACHED_PROCESS = 0x08000000
        subprocess.Popen([py_exe, 'ink_dbus.py',  'application', 'None', 'None', path_id_list_string, dbus_delay, selection_mode, current_selection_id_list_string], creationflags=DETACHED_PROCESS)
    else:
        subprocess.Popen(['python3', 'ink_dbus.py', 'application', 'None', 'None', path_id_list_string, dbus_delay, selection_mode, current_selection_id_list_string],
                         preexec_fn=os.setpgrp, stdout=open('/dev/null', 'w'),
                         stderr=open('/dev/null', 'w'), )


class SelectionPassback(inkex.EffectExtension):

    def add_arguments(self, pars):

        # Headline Settings

        pars.add_argument("--selection_mode_combo", type=str, dest="selection_mode_combo", default='clear')

        # Basic Page
        pars.add_argument("--selection_plus_notebook", type=str, dest="selection_plus_notebook", default=0)

        pars.add_argument("--selection_type_radio", type=str, dest="selection_type_radio", default='path')

        pars.add_argument("--dbus_delay_float", type=float, dest="dbus_delay_float", default=0.5)


        # Path Page

        pars.add_argument("--combined_paths_combo", type=str, dest="combined_paths_combo", default='ignore')

        pars.add_argument("--path_type_combo", type=str, dest="path_type_combo", default='absolute')

        pars.add_argument("--closed_path_combo", type=str, dest="closed_path_combo", default='ignore')

        pars.add_argument("--path_thres_bool", type=inkex.Boolean, dest="path_thres_bool", default=True)
        pars.add_argument("--path_thres_unit_choice_bool", type=inkex.Boolean, dest="path_thres_unit_choice_bool", default=False)
        pars.add_argument("--path_thres_unit_choice_combo", type=str, dest="path_thres_unit_choice_combo", default='px')
        pars.add_argument("--path_thres_radio", type=str, dest="path_thres_radio", default='node_count')

        pars.add_argument("--node_count_lower", type=float, dest="node_count_lower", default=16)
        pars.add_argument("--node_count_upper", type=float, dest="node_count_upper", default=16)

        pars.add_argument("--path_length_lower", type=float, dest="path_length_lower", default=16)
        pars.add_argument("--path_length_upper", type=float, dest="path_length_upper", default=16)

        pars.add_argument("--path_area_lower", type=float, dest="path_area_lower", default=16)
        pars.add_argument("--path_area_upper", type=float, dest="path_area_upper", default=16)

        pars.add_argument("--path_thres_sorting_combo", type=str, dest="path_thres_sorting_combo", default='ignore')

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

        pars.add_argument("--bbox_thres_type_combo", type=str, dest="bbox_thres_type_combo", default='px')

        pars.add_argument("--bbox_width_lower", type=float, dest="bbox_width_lower", default=16)
        pars.add_argument("--bbox_width_upper", type=float, dest="bbox_width_upper", default=16)

        pars.add_argument("--bbox_height_lower", type=float, dest="bbox_height_lower", default=16)
        pars.add_argument("--bbox_height_upper", type=float, dest="bbox_height_upper", default=16)

        pars.add_argument("--bbox_diagonal_lower", type=float, dest="bbox_diagonal_lower", default=16)
        pars.add_argument("--bbox_diagonal_upper", type=float, dest="bbox_diagonal_upper", default=16)

        pars.add_argument("--bbox_area_lower", type=float, dest="bbox_area_lower", default=16)
        pars.add_argument("--bbox_area_upper", type=float, dest="bbox_area_upper", default=16)

        pars.add_argument("--bbox_ratio_width_height_lower", type=float, dest="bbox_ratio_width_height_lower", default=16)
        pars.add_argument("--bbox_ratio_width_height_upper", type=float, dest="bbox_ratio_width_height_upper", default=16)

        pars.add_argument("--bbox_ratio_height_width_lower", type=float, dest="bbox_ratio_height_width_lower", default=16)
        pars.add_argument("--bbox_ratio_height_width_upper", type=float, dest="bbox_ratio_height_width_upper", default=16)

        pars.add_argument("--bbox_thres_sorting_combo", type=str, dest="bbox_thres_sorting_combo", default='ignore')

        # Colour Page

        # Swatch Options

        pars.add_argument("--draw_swatches_bool", type=inkex.Boolean, dest="draw_swatches_bool", default=True)
        pars.add_argument("--swatch_size_float", type=float, dest="swatch_size_float", default=5)
        pars.add_argument("--swatch_row_length_int", type=int, dest="swatch_row_length_int", default=16)

        # Simple Color limit

        pars.add_argument("--red_single_value_bool", type=inkex.Boolean, dest="red_single_value_bool", default=True)
        pars.add_argument("--red_single_value_int", type=int, dest="red_single_value_int", default=16)
        pars.add_argument("--red_single_value_more_than_bool", type=inkex.Boolean, dest="red_single_value_more_than_bool", default=True)

        pars.add_argument("--green_single_value_bool", type=inkex.Boolean, dest="green_single_value_bool", default=True)
        pars.add_argument("--green_single_value_int", type=int, dest="green_single_value_int", default=16)
        pars.add_argument("--green_single_value_more_than_bool", type=inkex.Boolean, dest="green_single_value_more_than_bool", default=True)

        pars.add_argument("--blue_single_value_bool", type=inkex.Boolean, dest="blue_single_value_bool", default=True)
        pars.add_argument("--blue_single_value_int", type=int, dest="blue_single_value_int", default=16)
        pars.add_argument("--blue_single_value_more_than_bool", type=inkex.Boolean, dest="blue_single_value_more_than_bool", default=True)

        # Colour ranges

        pars.add_argument("--color_thres_radio", type=str, dest="color_thres_radio", default='color_limit')

        pars.add_argument("--red_color_range_bool", type=inkex.Boolean, dest="red_color_range_bool", default=True)
        pars.add_argument("--red_color_range_lower_int", type=int, dest="red_color_range_lower_int", default=0)
        pars.add_argument("--red_color_range_upper_int", type=int, dest="red_color_range_upper_int", default=255)

        pars.add_argument("--green_color_range_bool", type=inkex.Boolean, dest="green_color_range_bool", default=True)
        pars.add_argument("--green_color_range_lower_int", type=int, dest="green_color_range_lower_int", default=0)
        pars.add_argument("--green_color_range_upper_int", type=int, dest="green_color_range_upper_int", default=255)

        pars.add_argument("--blue_color_range_bool", type=inkex.Boolean, dest="blue_color_range_bool", default=True)
        pars.add_argument("--blue_color_range_lower_int", type=int, dest="blue_color_range_lower_int", default=0)
        pars.add_argument("--blue_color_range_upper_int", type=int, dest="blue_color_range_upper_int", default=255)

        # Euclidean Weighting

        pars.add_argument("--eu_base_color_inkex_color", type=inkex.Color, dest="eu_base_color_inkex_color", default=0x0000ffff)

        pars.add_argument("--euclidean_weighting_radio", type=str, dest="euclidean_weighting_radio", default='1_1_1')

        pars.add_argument("--r_weight_int", type=int, dest="r_weight_int", default=1)
        pars.add_argument("--g_weight_int", type=int, dest="g_weight_int", default=1)
        pars.add_argument("--b_weight_int", type=int, dest="b_weight_int", default=1)

        pars.add_argument("--eu_threshold_float", type=float, dest="eu_threshold_float", default=5)


    def effect(self):

        current_selection_list = self.svg.selected

        id_list = []

        dbus_delay = str(self.options.dbus_delay_float)

        selection_mode = self.options.selection_mode_combo

        if self.options.selection_plus_notebook == 'settings_page':
            selection_string = f'//svg:{self.options.selection_type_radio}'
            try:
                elements = self.svg.xpath(selection_string)
            except:
                sys.exit()
            final_object_list = elements

        # Paths Page

        elif self.options.selection_plus_notebook == 'path_page':
            selection_string = f'//svg:path'
            path_list = self.svg.xpath(selection_string)

            final_object_list = SpPath.chain_path_criteria(self, path_list)

        elif self.options.selection_plus_notebook == 'xpath_page':
            selected_xpath_string = 'xpath_user_string' + self.options.xpath_string_radio

            xpath_string = getattr(self.options, selected_xpath_string)
            # selection_string = f'{self.options.xpath_string_input_box}'

            try:
                elements = self.svg.xpath(xpath_string)
            except:
                sys.exit()
            final_object_list = elements

        # Bounding Box Page

        elif self.options.selection_plus_notebook == 'bounding_box_page':
            selection_string = '//svg:circle | //svg:ellipse | //svg:line | //svg:text | //svg:tspan | //svg:path | //svg:polygon | //svg:polyline | //svg:rect'

            selection_list = self.svg.xpath(selection_string)

            final_object_list = SpBbox.bbox_thres(self, selection_list)

        elif self.options.selection_plus_notebook == 'color_page':

            final_object_list = SpColor.sp_colour_main(self)

        # Make an id list from the final object list.

        for path_object in final_object_list:
            id_list.append(path_object.get_id())


        # Command separated id string ( not a list )
        id_list_string = f"\'{','.join(id_list)}\'"

        current_selection_id_list = []

        for item in current_selection_list:
            current_selection_id_list.append(item.get_id())
        current_selection_id_list_string = f"\'{','.join(current_selection_id_list)}\'"

        # Call selection function

        pass_ids_to_dbus(self, id_list_string, dbus_delay, selection_mode, current_selection_id_list_string)

        sys.exit()

if __name__ == '__main__':
    SelectionPassback().run()
