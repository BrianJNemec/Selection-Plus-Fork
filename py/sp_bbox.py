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

from py.sp_util import SpUtil

import sys


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


class SpBbox:

    # ilist = initial list of elements

    def threshold_bool(self, value, lower_thres, upper_thres):
        if (lower_thres <= value <= upper_thres):
            return True
        else:
            return False

    def bbox_thres(self, ilist):

        # Should we also get the text bounding boxes ? (command call needed)

        if self.options.bbox_type_radio == 'geometric':
            # inkex.errormsg('query-all command call Geometric')
            SpUtil.query_all_to_bbox(self, self.svg, current_bbox_type='geo')
        elif self.options.bbox_type_radio == 'visual':
            # inkex.errormsg('query-all command call Visual')
            SpUtil.query_all_to_bbox(self, self.svg, current_bbox_type='vis')
        elif self.options.bbox_type_radio == 'geometric_no_text':
            for element in ilist:

                for item in ilist:
                    if item.TAG.lower() == 'text' or item.TAG.lower() == 'tspan':
                        ilist.remove(item)
                else:
                    SpUtil.populate_current_bbox_from_bounding_box(self, element)

        # User unit choice conversion
        # As we are now using query-all - which is pixel based have to change this
        # if self.options.bbox_unit_choice_bool:
        #     unit_choice = self.options.bbox_unit_choice_combo
        #     SpBbox.cf = conversions[unit_choice] / conversions[self.svg.unit]
        # else:
        #     SpBbox.cf = 1

        if self.options.bbox_unit_choice_bool:
            unit_choice = self.options.bbox_unit_choice_combo
            SpBbox.cf = 1 / conversions[unit_choice]
        else:
            SpBbox.cf = 1 / conversions[self.svg.unit]

        # Should we include text elements ?
        # for item in ilist:
        #     # inkex.errormsg(item.TAG)
        #     if item.TAG.lower() == 'text' or item.TAG.lower() == 'tspan':
        #         ilist.remove(item)

        # ilist_id_list = [x.get_id() for x in ilist]

        bbox_chained_thres_list = []

        thres_type = self.options.bbox_thres_type_combo

        thres_object_list = []

        # inkex.errormsg(thres_type)

        # Height Threshold
        if thres_type == 'bbox_width':
            for element in ilist:
                if SpBbox.thres_bbox_width(self, element, self.options.bbox_width_lower, self.options.bbox_width_upper):
                    thres_object_list.append(element)

        # Width Threshold
        if thres_type == 'bbox_height':
            for element in ilist:
                if SpBbox.thres_bbox_height(self, element, self.options.bbox_height_lower, self.options.bbox_height_upper):
                    thres_object_list.append(element)

        # Diagonal Threshold
        if thres_type == 'bbox_diagonal':
            for element in ilist:
                if SpBbox.thres_bbox_diagonal(self, element, self.options.bbox_diagonal_lower, self.options.bbox_diagonal_upper):
                    thres_object_list.append(element)

        # Area Threshold
        if thres_type == 'bbox_area':
            for element in ilist:
                if SpBbox.thres_bbox_area(self, element, self.options.bbox_area_lower, self.options.bbox_area_upper):
                    thres_object_list.append(element)

        # Width Height Ratio Threshold
        if thres_type == 'bbox_ratio_width_height':
            for element in ilist:
                if SpBbox.thres_bbox_ratio_width_height(self, element, self.options.bbox_ratio_width_height_lower, self.options.bbox_ratio_width_height_upper):
                    thres_object_list.append(element)

        # Height Width Ratio Threshold
        if thres_type == 'bbox_ratio_height_width':
            for element in ilist:
                if SpBbox.thres_bbox_ratio_height_width(self, element, self.options.bbox_ratio_height_width_lower, self.options.bbox_ratio_height_width_upper):
                    thres_object_list.append(element)

        if self.options.bbox_thres_sorting_combo != 'ignore':

            for item in thres_object_list:

                if self.options.bbox_thres_sorting_combo == 'descending':
                    reverse_bool = True
                else:
                    reverse_bool = False

                SpBbox.sort_thres_value(self, thres_object_list, reverse_bool)


        return thres_object_list

    def thres_bbox_width(self, element, lower_thres, upper_thres):

        bbox = element.current_bbox

        width = bbox.width * SpBbox.cf

        inkex.errormsg(f'lower thres {lower_thres} upper thres {upper_thres} width {width}')

        return SpBbox.threshold_bool(self, width, lower_thres, upper_thres)


    def thres_bbox_height(self, element, lower_thres, upper_thres):

        bbox = element.current_bbox

        inkex.errormsg(element.current_bbox.height)

        height = bbox.height * SpBbox.cf

        inkex.errormsg(f'lower thres {lower_thres}  height {height} upper thres {upper_thres}')

        return SpBbox.threshold_bool(self, height, lower_thres, upper_thres)

    def thres_bbox_diagonal(self, element, lower_thres, upper_thres):

        import math
        # bbox = element.bounding_box(True)
        bbox = element.current_bbox
        diagonal = round(math.sqrt((bbox.width**2) + (bbox.height**2)), 4) * SpBbox.cf

        inkex.errormsg(f'lower thres {lower_thres}  diagonal {diagonal} upper thres {upper_thres}')

        return SpBbox.threshold_bool(self, diagonal, lower_thres, upper_thres)


    def thres_bbox_area(self, element, lower_thres, upper_thres):

        # bbox = element.bounding_box(True)
        bbox = element.current_bbox
        area = (bbox.width * SpBbox.cf) * (bbox.height * SpBbox.cf)

        inkex.errormsg(f'{element.get_id()} within threshold - lower: {lower_thres} upper: {upper_thres} element_value: {area}')

        return SpBbox.threshold_bool(self, area, lower_thres, upper_thres)

    def thres_bbox_ratio_width_height(self, element, lower_thres, upper_thres):

        # bbox = element.bounding_box(True)

        bbox = element.current_bbox

        width = bbox.width
        height = bbox.height
        width_height_ratio = width / height

        return SpBbox.threshold_bool(self, width_height_ratio, lower_thres, upper_thres)


    def thres_bbox_ratio_height_width(self, element, lower_thres, upper_thres):

        # bbox = element.bounding_box(True)

        bbox = element.current_bbox

        width = bbox.width
        height = bbox.height
        height_width_ratio = height / width

        return SpBbox.threshold_bool(self, height_width_ratio, lower_thres, upper_thres)

    def sort_thres_value(self, path_list, reverse_bool):

        path_list.sort(key=lambda x: x.thres_value, reverse=reverse_bool)
        return path_list