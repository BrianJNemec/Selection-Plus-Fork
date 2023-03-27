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
# Ink Dbus- a dbus based inkscape extension
# An Inkscape 1.2.1+ extension
##############################################################################

import subprocess

import sys, os, zlib

import inkex

import warnings
warnings.filterwarnings("ignore")

# This statement to sent Gtk3 stderr away :)
import sys
tmp, sys.stderr = sys.stderr, None  # type: ignore


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



def call_sp_lasso(self, lasso_element_id, pixel_scale_value_int, svg_temp_filepath, temp_folder):

    if os_check(self) == 'windows':

        py_exe = sys.executable
        if 'pythonw.exe' in py_exe:
            py_exe = py_exe.replace('pythonw.exe', 'python.exe')

        DETACHED_PROCESS = 0x08000000
        subprocess.Popen([py_exe, 'sp_lasso.py', 'standalone', lasso_element_id, pixel_scale_value_int, svg_temp_filepath, temp_folder], creationflags=DETACHED_PROCESS)
    else:
        subprocess.Popen(['python3', 'sp_lasso.py', 'standalone', lasso_element_id, pixel_scale_value_int, svg_temp_filepath, temp_folder],
                         preexec_fn=os.setpgrp, stdout=open('/dev/null', 'w'),
                         stderr=open('/dev/null', 'w'))


class SelectionPassback(inkex.EffectExtension):

    def add_arguments(self, pars):
        pars.add_argument("--pixel_scale_value_int", type=float, dest="pixel_scale_value_int", default=300)

    def effect(self):

        lasso_element = self.svg.selected[0]

        lasso_element_id = lasso_element.get_id()

        import tempfile, os
        temp_folder = tempfile.mkdtemp()
        svg_temp_filepath = os.path.join(temp_folder, 'sp_tempfile.svg')

        with open(svg_temp_filepath, 'wb') as output_file:
            self.save(output_file)

        call_sp_lasso(self, lasso_element_id, str(self.options.pixel_scale_value_int), str(svg_temp_filepath), str(temp_folder))

        sys.exit()


if __name__ == '__main__':
    SelectionPassback().run()
