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
import uuid

import inkex
import gi
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import GdkPixbuf

from PIL import Image, ImageChops

import numpy as np
import sys, shutil, tempfile, os


def rect_from_bbox(self, bbox, stroke_color):
    from inkex import Rectangle
    rect = Rectangle()
    rect.set('x', bbox.left)
    rect.set('y', bbox.top)
    rect.set('width', bbox.width)
    rect.set('height', bbox.height)
    rect.set('stroke', stroke_color)
    rect.set('fill', 'none')

    self.svg.get_current_layer().append(rect)


class SpLasso:

    def element_to_pixbuf(self, element):

        # Lets try to fix errors at very small values

        pixel_scale_bool = True

        if pixel_scale_bool:

            min_x = SpLasso.lasso_bbox.left
            min_y = SpLasso.lasso_bbox.top
            width = SpLasso.lasso_bbox.width
            height = SpLasso.lasso_bbox.height

            view_box_list = [min_x, min_y, width, height]
            view_box_string_list = [str(x) for x in view_box_list]
            view_box = ' '.join(view_box_string_list)
            element.set('viewBox', view_box)

            page_bbox = self.svg.get_page_bbox()
            page_width = page_bbox.width
            page_height = page_bbox.height
            # We want max width of 1000 pixels
            aspect_ratio = page_width / page_height
            SpLasso.pixel_scale_value_int = 500
            new_page_width = SpLasso.pixel_scale_value_int
            new_page_height = new_page_width / aspect_ratio
            element.set('width', f'{new_page_width}px')
            element.set('height', f'{new_page_height}px')


        element = element.tostring()

        loader = GdkPixbuf.PixbufLoader()
        loader.write(element)
        loader.close()
        pixbuf = loader.get_pixbuf()
        return pixbuf

    def pixbuf_to_pil(self, pixbuf):

        fudge_factor = 1.0675

        width, height = pixbuf.get_width(), pixbuf.get_height()

        # there is an unexplained size difference between svg canvas
        # and the resulting bitmap size, lets correct pixbuf
        scaled_width = int(width * fudge_factor)
        scaled_height = int(height * fudge_factor)

        pixbuf = pixbuf.scale_simple(scaled_width, scaled_height, GdkPixbuf.InterpType.BILINEAR)

        return Image.frombytes("RGBA", (scaled_width, scaled_height), pixbuf.get_pixels())

    def solo_element(svg, element):

        item_list = svg.xpath('//svg:circle | //svg:ellipse | //svg:line | //svg:path | //svg:text | //svg:polygon | //svg:polyline | //svg:rect | //svg:use | //svg:image')

        for item in item_list:

            if item.getparent().TAG != 'clipPath':
                item.style['display'] = 'none'

        if 'display' in element.style.keys():
            inkex.errormsg('found display')
            element.style.pop('display')

    def make_bitmap_list(self, element_list, lasso=False):

        pil_bitmap_list = []

        for element in element_list:
            from copy import deepcopy
            svg_copy = deepcopy(self.svg)
            element_copy = svg_copy.getElementById(element.get_id())

            # Lets unlink if object is a clone, otherwise
            # object will vanish and not soloed
            if element_copy.TAG == 'use':
                element_copy = element_copy.unlink()

            inkex.errormsg(element_copy.style)

            if lasso:
                element_copy.style['stroke'] = 'none'
                element_copy.style['fill'] = 'green'
            else:
                element_copy.style['stroke'] = 'green'
                element_copy.style['fill'] = 'green'

            SpLasso.solo_element(svg_copy, element_copy)

            inkex.errormsg(element_copy.style)

            pixbuf = SpLasso.element_to_pixbuf(self, svg_copy)
            im = SpLasso.pixbuf_to_pil(self, pixbuf)

            pil_bitmap_list.append(im)

        # for image in pil_bitmap_list:
        #     random_file_name = str(uuid.uuid4())
        #     image.save(os.path.join(SpLasso.temp_folder, random_file_name), 'png')


        return pil_bitmap_list

    def get_inside_bbox(self, lasso_element, element_list):

        inside_list = []

        lasso_bbox = lasso_element.bounding_box(True)

        element_list.remove(lasso_element)

        for element in element_list:

            # workaround for clipath bug !
            if 'clip-path' in element.attrib.keys():
                element_bbox = element.bounding_box()

            elif element.TAG == 'use':
                clone_dupe = element.duplicate()
                unlinked_clone = clone_dupe.unlink()
                element_bbox = unlinked_clone.bounding_box()
                unlinked_clone.delete()

            else:
                element_bbox = element.bounding_box(True)

            if (element_bbox.top < lasso_bbox.top):
                continue
            elif (element_bbox.bottom > lasso_bbox.bottom):
                continue
            elif (element_bbox.left < lasso_bbox.left):
                continue
            elif (element_bbox.right > lasso_bbox.right):
                continue
            else:
                inside_list.append(element)

        # inkex.errormsg(inside_list)

        id_list = [x.get_id() for x in inside_list]
        inkex.errormsg(id_list)

        return inside_list

    def make_two_color_pil(self, pil_image):

        two_color_pil = pil_image.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=2)
        two_color_pil.putpalette([255, 255, 255, 0, 0, 0])

        return two_color_pil

    def make_lasso_select_list(self, lasso_element):

        lasso_list = []

        element_list = self.svg.xpath('//svg:circle | //svg:ellipse | //svg:line | //svg:path | //svg:polygon | //svg:polyline | //svg:rect | //svg:use | //svg:image')

        inside_bbox_list = SpLasso.get_inside_bbox(self, lasso_element, element_list)

        pil_image_list = SpLasso.make_bitmap_list(self, inside_bbox_list)

        lasso_pil_image = SpLasso.make_bitmap_list(self, [lasso_element], True)[0]

        two_color_lasso_pil = SpLasso.make_two_color_pil(self, lasso_pil_image)

        random_file_name = str(uuid.uuid4())
        two_color_lasso_pil.save(os.path.join(SpLasso.temp_folder, random_file_name), 'png')

        im_matrix = np.array(two_color_lasso_pil)

        unique, counts = np.unique(im_matrix, return_counts=True)

        lasso_count = counts.tolist()[0]


        for pil_image, inside_element in zip(pil_image_list, inside_bbox_list):

            two_color_pil = SpLasso.make_two_color_pil(self, pil_image)

            # random_file_name = str(uuid.uuid4())
            # two_color_pil.save(os.path.join(SpLasso.temp_folder, random_file_name), 'png')

            image_diff = ImageChops.logical_or(two_color_lasso_pil.convert("1"), two_color_pil.convert("1"))

            im_matrix = np.array(image_diff)

            unique, counts = np.unique(im_matrix, return_counts=True)

            count_list = counts.tolist()

            if len(count_list) < 2:
                continue
            else:
                image_pixel_count = count_list[1]

            if image_pixel_count == lasso_count:
                lasso_list.append(inside_element)

        return lasso_list

    def return_lasso_select_list(self, lasso_element):

        # Lets store the lasso_bbox so we can alter the viewbox
        # of the svg to prevent tiny objects from being misread
        # when in raster form

        SpLasso.lasso_bbox = lasso_element.bounding_box(True)

        lasso_list = SpLasso.make_lasso_select_list(self, lasso_element)

        id_list = [x.get_id() for x in lasso_list]

        return id_list


class SelectionPlusLasso(inkex.EffectExtension):

    def effect(self):

        lasso_element = self.svg.selected[0]

        SpLasso.return_lasso_select_list(self, lasso_element)

        # sys.exit()


class DummySelf:
    pass

# Lets check if this is to be a standalone window
import sys
if 'standalone' in sys.argv:

    lasso_element_id = sys.argv[2]

    current_selection_id_list_string = sys.argv[3]

    current_selection_id_list = current_selection_id_list_string.split(',')

    SpLasso.pixel_scale_value_int = int(float(sys.argv[4]))

    selection_mode = sys.argv[5]

    svg_temp_filepath = sys.argv[6]

    temp_folder = sys.argv[7]

    SpLasso.temp_folder = temp_folder

    svg_element = inkex.load_svg(svg_temp_filepath).getroot()

    dummy_self = DummySelf()

    dummy_self.svg = svg_element

    lasso_element = dummy_self.svg.getElementById(lasso_element_id)

    id_list = SpLasso.return_lasso_select_list(dummy_self, lasso_element)

    from ink_dbus import InkDbus

    InkDbus.call_dbus_selection(None, id_list, current_selection_id_list, selection_mode, 0.5)

    # Remove Temp Folder
    if hasattr(SpLasso, 'temp_folder'):
        shutil.rmtree(SpLasso.temp_folder)

    sys.exit()


if __name__ == '__main__':
    SelectionPlusLasso().run()