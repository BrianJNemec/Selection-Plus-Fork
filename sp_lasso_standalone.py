#!/usr/bin/env python
# coding=utf-8
#
# Copyright (C) [2023] [Matt Cottam], [mpcottam@raincloud.co.uk]
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
# Ink Lasso - a dbus based inkscape extension
# An Inkscape 1.2.1+ extension
##############################################################################
import shutil
import subprocess

import sys, os, zlib

import inkex

import warnings
warnings.filterwarnings("ignore")

# This statement to sent Gtk3 stderr away :)
import sys


import logging
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

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



def call_sp_lasso(self, lasso_element_id, current_selection_id_list_string, pixel_scale_value_int,  selection_mode, svg_temp_filepath, temp_folder):

    if os_check(self) == 'windows':

        py_exe = sys.executable
        if 'pythonw.exe' in py_exe:
            py_exe = py_exe.replace('pythonw.exe', 'python.exe')

        DETACHED_PROCESS = 0x08000000
        subprocess.Popen([py_exe, 'sp_lasso.py', 'standalone', lasso_element_id, current_selection_id_list_string,
                          pixel_scale_value_int, selection_mode, svg_temp_filepath, temp_folder], creationflags=DETACHED_PROCESS)
    else:
        subprocess.Popen(['python3', 'sp_lasso.py', 'standalone', lasso_element_id, current_selection_id_list_string,
                          pixel_scale_value_int,  selection_mode, svg_temp_filepath, temp_folder],
                         preexec_fn=os.setpgrp, stdout=open('/dev/null', 'w'),
                         stderr=open('/dev/null', 'w'))


class SelectionPassback(inkex.EffectExtension):

    def add_arguments(self, pars):
        pars.add_argument("--pixel_scale_value_int", type=float, dest="pixel_scale_value_int", default=300)

        pars.add_argument("--selection_mode_combo", type=str, dest="selection_mode_combo", default='clear')

        pars.add_argument("--text_cb", type=inkex.Boolean, dest="text_cb", default=True)

    def effect(self):

        selection_list = self.svg.selected

        if len(selection_list) < 1:
            inkex.errormsg('At least one selected object is require to lasso :)')
            return

        lasso_element = selection_list[-1]

        lasso_element_id = lasso_element.get_id()

        # Remove the lasso from the selection list
        selection_list.pop(-1)
        current_selection_list = selection_list

        current_selection_id_list = [x.get_id() for x in current_selection_list]

        current_selection_id_list_string = ','.join(current_selection_id_list)

        pixel_scale_value_int = str(self.options.pixel_scale_value_int)

        selection_mode = self.options.selection_mode_combo

        import tempfile, os
        temp_folder = tempfile.mkdtemp()

        # sys.exit()

        # temp_folder = temp_folder.name

        os.chmod(temp_folder, 0o0777)

        svg_temp_filepath = os.path.join(temp_folder, 'sp_tempfile.svg')

        with open(svg_temp_filepath, 'wb') as output_file:
            self.save(output_file)

        # for file in os.listdir(temp_folder):
        #
        #     filepath = os.path.join(temp_folder, file)
        #
        #     os.chmod(filepath, 0o0777)

        # Should be use a command call to convert text elements to
        # combined path elements ?
        # text-to-path creates a group with individual letter paths
        # so need to use path-union for each text element instead
        # to get combined path for each text element

        svg_temp_union_filepath = os.path.join(temp_folder, 'sp_tempfile_union.svg')

        text_bool = self.options.text_cb

        if text_bool:

            # Make list of text elements to pass to inkscape command line
            text_elements = self.svg.xpath('//svg:text')
            text_elements_id_list = [x.get_id() for x in text_elements]
            # text_elements_id_string = ','.join(text_elements_id_list)

            union_actions_string = ''
            for item in text_elements_id_list:
                union_actions_string += f'select-by-id:{item};path-union;select-clear;'

            my_actions = '--actions='
            export_union_actions = my_actions + f'export-filename:{svg_temp_union_filepath};{union_actions_string}export-do;'

            inkex.command.inkscape(svg_temp_filepath, export_union_actions)

            svg_temp_filepath = svg_temp_union_filepath

        call_sp_lasso(self, lasso_element_id, current_selection_id_list_string, pixel_scale_value_int,  selection_mode, str(svg_temp_filepath), str(temp_folder))

        sys.exit()


if __name__ == '__main__':
    SelectionPassback().run()
