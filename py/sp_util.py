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

class SpUtil:

    class uBbox():
        def get_bbox(self, dict):
            for key, value in dict.items():
                setattr(self, key, value)


    def populate_geo_bbox_from_bbox_dict(self, element, geo_bbox_dict):

        element.geo_bbox = SpUtil.uBbox()
        for key, value in geo_bbox_dict.items():
            element.geo_bbox.__setattr__(key, value)

    def populate_vis_bbox_from_bbox_dict(self, element, vis_bbox_dict):

        element.vis_bbox = SpUtil.uBbox()
        for key, value in vis_bbox_dict.items():
            element.vis_bbox.__setattr__(key, value)

    def populate_current_bbox_from_bounding_box(self, element):
        bbox = element.bounding_box(True)
        current_bbox_dict = {'area': bbox.area, 'bottom': bbox.bottom, 'center': bbox.center, 'center_x': bbox.center_x, 'center_y': bbox.center_y, 'height': bbox.height, 'left': bbox.left, 'right': bbox.right, 'width': bbox.width}

        # element.bounding_box() returns user units, need this in pixels so it
        # will work with the same function as the query-all results
        for key, value in current_bbox_dict.items():
            current_bbox_dict[key] = value * conversions[self.svg.unit]

        element.current_bbox = SpUtil.uBbox()
        for key, value in current_bbox_dict.items():
            element.current_bbox.__setattr__(key, value)


    def query_all_to_bbox(self, input_svg, current_bbox_type='geo'):

        # Lets get both visual and geometric bboxes from query--all at
        # the same time.

        # first lets duplicate the svg

        from copy import deepcopy
        from uuid import uuid4

        id_suffix = f'_{uuid4()}'

        new_svg = deepcopy(input_svg)
        drawable_elements = new_svg.xpath('//svg:circle | //svg:ellipse | //svg:line | //svg:path | //svg:text | //svg:tspan | //svg:polygon | //svg:polyline | //svg:rect | //svg:use | //svg:image')

        # Create a set of duplicate elements
        # remove all attributes which contribute to visual bbox
        # That leaves us with a set of geometric and visual bboxes
        visual_attr_list = ['style', 'fill', 'stroke', 'filter']
        for element in drawable_elements:
            geo_element = element.duplicate()
            for visual_attr in visual_attr_list:
                if geo_element.attrib.get(visual_attr):
                    geo_element.attrib.pop(visual_attr)
            geo_element.set('id', element.get('id') + id_suffix)



        new_svg_input_file, temp_file_path = SpUtil.make_temp_file_from_svg_object(self, new_svg)

        new_svg_input_file.close()

        q_bbox = SpUtil.inkscape_command_call_bboxes_to_dict(self, temp_file_path)

        for element in drawable_elements:

            _id = element.get_id()

            if _id in q_bbox.keys():

                my_object = input_svg.getElementById(_id)

                area = q_bbox[_id]['width'] * q_bbox[_id]['height']
                bottom = q_bbox[_id]['y4']
                center = q_bbox[_id]['mid_x'], q_bbox[_id]['mid_y']
                center_x = q_bbox[_id]['mid_x']
                center_y = q_bbox[_id]['mid_y']
                height = q_bbox[_id]['height']
                width = q_bbox[_id]['width']
                left = q_bbox[_id]['x1']
                right = q_bbox[_id]['x2']

                vis_bbox_dict = {'area': area, 'bottom': bottom, 'center': center, 'center_x': center_x, 'center_y': center_y, 'height': height, 'left': left, 'right': right, 'width': width}
                SpUtil.populate_vis_bbox_from_bbox_dict(self, my_object, vis_bbox_dict)

                geo_area = q_bbox[f'{_id}{id_suffix}']['width'] * q_bbox[f'{_id}{id_suffix}']['height']
                geo_bottom = q_bbox[f'{_id}{id_suffix}']['y4']
                geo_center = q_bbox[f'{_id}{id_suffix}']['mid_x'], q_bbox[f'{_id}{id_suffix}']['mid_y']
                geo_center_x = q_bbox[f'{_id}{id_suffix}']['mid_x']
                geo_center_y = q_bbox[f'{_id}{id_suffix}']['mid_y']
                geo_height = q_bbox[f'{_id}{id_suffix}']['height']
                geo_width = q_bbox[f'{_id}{id_suffix}']['width']
                geo_left = q_bbox[f'{_id}{id_suffix}']['x1']
                geo_right = q_bbox[f'{_id}{id_suffix}']['x2']

                geo_bbox_dict = {'area': geo_area, 'bottom': geo_bottom, 'center': geo_center, 'center_x': geo_center_x, 'center_y': geo_center_y, 'height': geo_height, 'left': geo_left, 'right': geo_right, 'width': geo_width}
                SpUtil.populate_geo_bbox_from_bbox_dict(self, my_object, geo_bbox_dict)

                if current_bbox_type == 'geo':
                    my_object.current_bbox = my_object.geo_bbox
                else:
                    my_object.current_bbox = my_object.vis_bbox

    def inkscape_command_call_bboxes_to_dict(self, input_file):
        """
        A function to return a dictionary of all element bounding boxes
        -- this function is visual ( includes stroke etc ) rather than just
        geometric ( just path bbox ) \n
        :param input_file: input file path ( usually self.options.input_file )
        :return: Returns the results of --query-all in a dictionary
        """
        from inkex import command
        # First make a copy of the input_file
        temp_svg, temp_file_path = SpUtil.make_temp_file_copy(self, input_file)
        # Then run the command line
        my_query = command.inkscape(temp_svg.name, '--query-all')

        # Account for versions of inkey.py which return query as bytes
        if type(my_query) != str:
            my_query = my_query.decode("utf-8")
        # --query-all produces multiline output of the following format
        # path853,172.491,468.905,192.11,166.525 - as string
        # ElementId, Top, Left, Width, Height

        # Make a list splitting by each new line
        my_query_items = my_query.split('\n')
        my_element_bbox_dict = {}

        for my_query_item in my_query_items:
            # Create a comma separated list item for each line
            my_element = my_query_item.split(',')
            # Make a dictionary for all elements, rejected malformed elements.
            if len(my_element) > 4:
                my_element_bbox_dict[my_element[0]] = {}
                # Create Dictionary entry in anticlockwise format
                # x1 = TopLeft, x2 = BottomLeft, x3 = BottomRight, x4 = TopRight, mid_x and mid_y

                # First convert all values to float, skipping element id ( first entry )
                my_element_bbox = [float(x) for x in my_element[1:]]

                width = my_element_bbox[2]
                height = my_element_bbox[3]

                x1 = my_element_bbox[0]
                y1 = my_element_bbox[1]
                x2 = x1
                y2 = y1 + height
                x3 = x1 + width
                y3 = y2
                x4 = x1 + width
                y4 = y1
                mid_x = x1 + width / 2
                mid_y = y1 + height / 2

                my_element_bbox_dict[my_element[0]].update(x1=x1, y1=y1, x2=x2, y2=y2, x3=x3, y3=y3, x4=x4, y4=y4,
                                                           mid_x=mid_x, mid_y=mid_y, width=width, height=height)
        # Return dictionary
        temp_svg.close()
        return my_element_bbox_dict

    def make_temp_file_from_svg_object(self, svg_object):
        import os
        import time, uuid
        temp_file_name = str(uuid.uuid4()) + '.svg'
        # temp_file_name = str(time.time()).replace('.', '') + '.svg'
        svg_text = svg_object.tostring().decode('utf-8')
        if hasattr(self, 'inklin_temp_folder'):
            temp_folder = self.inklin_temp_folder
        else:
            temp_folder = SpUtil.make_temp_folder(self)
        temp_file_path = os.path.join(temp_folder, temp_file_name)
        new_file = open(temp_file_path, 'w')
        new_file.write(svg_text)

        return new_file, temp_file_path

    def make_temp_folder(self):
        """
        Creates a temp folder to which files can be written \n
        To remove folder at end of script use: \n
        # Cleanup temp folder \n
        if hasattr(self, 'inklin_temp_folder'):
            shutil.rmtree(self.inklin_temp_folder)

        :return: A temp folder path string
        """
        import tempfile
        temp_folder = tempfile.mkdtemp()
        self.inklin_temp_folder = str(temp_folder)
        return temp_folder

    def make_temp_file_copy(self, my_file, extension='.svg'):
        """
        :param my_file: file to make temp copy of
        :param extension: file extension to append to new filename
        :return: temp_file_object (open) , temp_file_path
        """
        import sys
        import shutil
        import os
        import uuid
        # Create random uuid - then add extension
        temp_file_name = str(uuid.uuid4()) + str(extension)
        if hasattr(self, 'inklin_temp_folder'):
            temp_folder = self.inklin_temp_folder
        else:
            temp_folder = SpUtil.make_temp_folder(self)
        temp_file_path = os.path.join(temp_folder, temp_file_name)
        temp_file = shutil.copy(my_file, temp_file_path)
        temp_file_object = open(temp_file)
        temp_file_object.temp_folder = temp_folder
        return temp_file_object, temp_file_path