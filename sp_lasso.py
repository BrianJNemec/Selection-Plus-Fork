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
import gi
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import GdkPixbuf

from PIL import Image, ImageChops

import numpy as np
import sys, shutil

import selection_plus
#
# selection_plus.set_stdout(None, 'off')
# selection_plus.set_stderr(None, 'off')
# tmp, sys.stderr = sys.stderr, None  # type: ignore

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

            # write_debug_file(f'width {width} height {height}')

            write_debug_file(self.svg.get('viewBox'))

            svg_width = element.get('width')
            svg_height = element.get('height')

            page_bbox = self.svg.get_page_bbox()
            page_width = page_bbox.width
            page_height = page_bbox.height
            # We want max width of 1000 pixels
            aspect_ratio = page_width / page_height
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
            item.style['display'] = 'none'
            # inkex.errormsg(item.style)
        element.style.pop('display')

    def make_bitmap_list(self, element_list):

        pil_bitmap_list = []

        for element in element_list:
            from copy import deepcopy
            svg_copy = deepcopy(self.svg)
            element_copy = svg_copy.getElementById(element.get_id())

            # Lets unlink if object is a clone, otherwise
            # object will vanish and not soloed
            if element_copy.TAG == 'use':
                element_copy = element_copy.unlink()

            element_copy.style['stroke'] = 'green'
            element_copy.style['fill'] = 'green'

            SpLasso.solo_element(svg_copy, element_copy)


            pixbuf = SpLasso.element_to_pixbuf(self, svg_copy)
            im = SpLasso.pixbuf_to_pil(self, pixbuf)

            pil_bitmap_list.append(im)


        return pil_bitmap_list

    def get_inside_bbox(self, lasso_element, element_list):

        inside_list = []

        lasso_bbox = lasso_element.bounding_box(True)

        element_list.remove(lasso_element)

        for element in element_list:

            # inkex.errormsg('-----------------------')
            # inkex.errormsg(element.get_id())
            # inkex.errormsg('-----------------------')

            # workaround for clipath bug !
            if 'clip-path' in element.attrib.keys():
                continue

            elif element.TAG == 'use':
                clone_dupe = element.duplicate()
                unlinked_clone = clone_dupe.unlink()
                element_bbox = unlinked_clone.bounding_box(True)
                unlinked_clone.delete()
                # inkex.errormsg(element_bbox)
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

        return inside_list

    def make_two_color_pil(self, pil_image):

        two_color_pil = pil_image.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=2)
        two_color_pil.putpalette([255, 255, 255, 0, 0, 0])

        return two_color_pil

    def make_lasso_select_list(self, lasso_element):

        lasso_list = []

        element_list = self.svg.xpath('//svg:circle | //svg:ellipse | //svg:line | //svg:path | //svg:polygon | //svg:polyline | //svg:rect | //svg:use | //svg:image')

        inside_bbox_list = SpLasso.get_inside_bbox(self, lasso_element, element_list)

        # inkex.errormsg(f'inside bbox list {inside_bbox_list}')

        pil_image_list = SpLasso.make_bitmap_list(self, inside_bbox_list)

        lasso_pil_image = SpLasso.make_bitmap_list(self, [lasso_element])[0]

        two_color_lasso_pil = SpLasso.make_two_color_pil(self, lasso_pil_image)

        im_matrix = np.array(two_color_lasso_pil)

        unique, counts = np.unique(im_matrix, return_counts=True)

        lasso_count = counts.tolist()[0]


        for pil_image, inside_element in zip(pil_image_list, inside_bbox_list):

            two_color_pil = SpLasso.make_two_color_pil(self, pil_image)

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

        # inkex.errormsg(f'lasso_list {lasso_list}')

        id_list = [x.get_id() for x in lasso_list]

        # Command separated id string ( not a list )
        id_list_string = f"\'{','.join(id_list)}\'"

        selection_plus.pass_ids_to_dbus(self, id_list_string, '0.5', 'clear', '')


# Needed to write debug info - as not possible to see subprocess
# stdout / stderr in Inkscape

def write_debug_file(data):
    with open("/home/name/test.txt", mode='a', encoding='utf-8') as file:
        file.write(str(data))
        file.close()

class SelectionPlusLasso(inkex.EffectExtension):

    def effect(self):

        lasso_element = self.svg.selected[0]

        SpLasso.return_lasso_select_list(self, lasso_element)

        sys.exit()


class DummySelf:
    pass

# Lets check if this is to be a standalone window
import sys
if 'standalone' in sys.argv:

    write_debug_file('hello')

    lasso_element_id = sys.argv[-4]

    SpLasso.pixel_scale_value_int = int(float(sys.argv[-3]))

    svg_temp_filepath = sys.argv[-2]

    temp_folder = sys.argv[-1]

    # write_debug_file(f'lasso {lasso_element_id}  {SpLasso.pixel_scale_value_int}  {svg_temp_filepath}  {temp_folder}')
    #
    # sys.exit()

    svg_element = inkex.load_svg(svg_temp_filepath).getroot()

    dummy_self = DummySelf()

    dummy_self.svg = svg_element

    lasso_element = dummy_self.svg.getElementById(lasso_element_id)

    SpLasso.return_lasso_select_list(dummy_self, lasso_element)

    # Remove Temp Folder
    shutil.rmtree(temp_folder)

    sys.exit()


if __name__ == '__main__':
    SelectionPlusLasso().run()