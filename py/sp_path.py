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

import inkex
from inkex.bezier import csparea, cspcofm, csplength
from copy import deepcopy

conversions = {
    'in': 96.0,
    'pt': 1.3333333333333333,
    'px': 1.0,
    'mm': 3.779527559055118,
    'cm': 37.79527559055118,
    'm': 3779.527559055118,
    'km': 3779527.559055118,
    'Q': 0.94488188976378,
    'pc': 16.0,
    'yd': 3456.0,
    'ft': 1152.0,
    '': 1.0,  # Default px
}

class SpPath:

    def threshold_bool(self, value, lower_thres, upper_thres):
        if (lower_thres <= value <= upper_thres):
            return True
        else:
            return False

    # For chain path criteria, some selections
    # exclude others - so cannot simply add
    # have to cascade and shrink the list each time

    def chain_path_criteria(self, path_list):

        # User unit choice conversion
        if self.options.path_thres_unit_choice_bool:
            unit_choice = self.options.path_thres_unit_choice_combo
            SpPath.cf = conversions[unit_choice] / conversions[self.svg.unit]
        else:
            SpPath.cf = 1

        def threshold_bool(self, value, lower_thres, upper_thres):
            if (lower_thres <= value <= upper_thres):
                return True
            else:
                return False

        current_path_list = deepcopy(path_list)

        if self.options.combined_paths_combo != 'ignore':
            combined_path_list = SpPath.filter_combined_paths(self, path_list)
            if self.options.combined_paths_combo != 'combined_only':
                current_path_list = [x for x in current_path_list if x in combined_path_list]
            else:
                current_path_list = [x for x in current_path_list if x not in combined_path_list]

        if self.options.closed_path_combo != 'ignore':
            closed_type = self.options.closed_path_combo
            closed_path_list = SpPath.filter_closed_paths(self, current_path_list)
            if closed_type == 'closed_only':
                current_path_list = [x for x in current_path_list if x in closed_path_list]
            else:
                current_path_list = [x for x in current_path_list if x not in closed_path_list]


        if self.options.path_type_combo != 'any':

            filter_type = self.options.path_type_combo
            path_type_list = SpPath.filter_paths_type(self, current_path_list, filter_type)

            current_path_list = [x for x in current_path_list if x in path_type_list]

        if self.options.path_thres_bool:

            if self.options.path_thres_radio == 'node_count':

                node_path_list = SpPath.paths_thres_node_count(self, current_path_list)
                current_path_list = [x for x in current_path_list if x in node_path_list]

            elif self.options.path_thres_radio == 'path_length':

                path_length_list = SpPath.paths_thres_path_length(self, current_path_list)
                current_path_list = [x for x in current_path_list if x in path_length_list]

            elif self.options.path_thres_radio == 'path_area':

                path_area_list = SpPath.paths_thres_path_area(self, current_path_list)
                current_path_list = [x for x in current_path_list if x in path_area_list]

            # Lets sort by thres_value and mark

            if self.options.path_thres_sorting_combo != 'ignore':

                for item in current_path_list:
                    #     inkex.errormsg(f'{item.get_id()}  {item.thres_value}')
                    #
                    # inkex.errormsg('-------------------------')

                    if self.options.path_thres_sorting_combo == 'descending':
                        reverse_bool = True
                    else:
                        reverse_bool = False

                    SpPath.sort_thres_value(self, current_path_list, reverse_bool)
                    #
                    # for item in path_length_list:
                    #     inkex.errormsg(f'{item.get_id()}  {item.thres_value}')

        return current_path_list


    # Just leave path letter commands
    def return_alphabet_string_only(self, my_string):
        import re
        regex = re.compile('[^a-zA-Z]')
        alphabet_string = regex.sub('', my_string)
        return(alphabet_string)

    def filter_paths_type(self, path_list, filter_type):

        path_type_list = []

        for path_object in path_list:
            path_type = SpPath.check_path_type(self, path_object)
            if path_type == filter_type:
                path_type_list.append(path_object)

        return path_type_list

    def filter_closed_paths(self, path_list):
        closed_path_list = []
        for path_object in path_list:
            if SpPath.check_closed_path(self, path_object):
                closed_path_list.append(path_object)
        return closed_path_list

    # Check for closed paths
    def check_closed_path(self, path_object):
        # Lets lower so we cover z and Z
        path_d = path_object.get('d').lower()
        z_list = path_d.strip().rfind('z')
        if z_list > 0:
            return True

    # Check for path type Any/Absolute/Relative/Mixed
    def check_path_type(self, path_object):

        d = path_object.get('d')
        upper_bool = d.isupper()
        lower_bool = d.islower()

        # inkex.errormsg(f'Upper {upper_bool} Lower {lower_bool}')

        if upper_bool:
            path_type = 'absolute'
        if lower_bool:
            path_type = 'relative'
        if not upper_bool and not lower_bool:
            path_type = 'mixed'

        return path_type

    def filter_combined_paths(self, path_list):
        combined_path_list = []
        for path_object in path_list:
            if SpPath.check_combined_path(self, path_object):
                combined_path_list.append(path_object)
        return combined_path_list


    def check_combined_path(self, path_object):
        d = path_object.get('d')
        combined_path_bool = d.lower().count('m') > 1
        return combined_path_bool


    def paths_thres_node_count(self, path_list):

        node_path_list = []

        lower_thres = self.options.node_count_lower
        upper_thres = self.options.node_count_upper

        for path_object in path_list:
            thres_bool = SpPath.thres_node_count(self, path_object, lower_thres, upper_thres)
            if thres_bool:
                node_path_list.append(path_object)

        return node_path_list

    def thres_node_count(self, path_object, lower_thres, upper_thres):

        node_count = SpPath.get_node_count(self, path_object)

        # Attach the thres Value to the object to allow sorting
        path_object.thres_value = node_count

        return SpPath.threshold_bool(self, node_count, lower_thres, upper_thres)


    def get_node_count(self, path_object):

        # end_points is a generator
        node_count = 0
        # z or Z indicates a closed path
        z_count = path_object.get('d').lower().count('z')
        # inkex.errormsg(z_count)
        for node in path_object.path.end_points:
            node_count += 1
        # We have to minus a node for each 'z'
        # closed path to make inkex match the gui
        node_count = node_count - (z_count * 2)

        return node_count

    def paths_thres_path_length(self, path_list):

        path_length_list = []

        lower_thres = self.options.path_length_lower
        upper_thres = self.options.path_length_upper

        for path_object in path_list:
            thres_bool = SpPath.thres_path_length(self, path_object, lower_thres, upper_thres)
            if thres_bool:
                path_length_list.append(path_object)


        return path_length_list


    def thres_path_length(self, path_object, lower_thres, upper_thres):

        csp = path_object.path.transform(path_object.composed_transform()).to_superpath()
        slengths, stotal = csplength(csp)

        stotal /= SpPath.cf

        # Attach the thres Value to the object to allow sorting
        path_object.thres_value = stotal

        # inkex.errormsg(f'lower {lower_thres} stotal {stotal} upper {upper_thres}')

        return SpPath.threshold_bool(self, stotal, lower_thres, upper_thres)

    # Area

    def paths_thres_path_area(self, path_list):

        path_area_list = []

        lower_thres = self.options.path_area_lower
        upper_thres = self.options.path_area_upper

        for path_object in path_list:
            thres_bool = SpPath.thres_path_area(self, path_object, lower_thres, upper_thres)
            # inkex.errormsg(thres_bool)
            if thres_bool:
                path_area_list.append(path_object)

        return path_area_list


    def thres_path_area(self, path_object, lower_thres, upper_thres):

        csp = path_object.path.transform(path_object.composed_transform()).to_superpath()
        stotal = abs(csparea(csp))

        stotal = stotal / (SpPath.cf**2)

        # Attach the thres Value to the object to allow sorting
        path_object.thres_value = stotal

        # inkex.errormsg(f'lower {lower_thres} stotal {stotal} upper {upper_thres}')

        return SpPath.threshold_bool(self, stotal, lower_thres, upper_thres)

    def sort_thres_value(self, path_list, reverse_bool):

        path_list.sort(key=lambda x: x.thres_value, reverse=reverse_bool)
        return path_list
