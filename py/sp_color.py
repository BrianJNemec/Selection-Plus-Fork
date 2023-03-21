import inkex
from inkex import Layer, PathElement
import math
import time
from copy import deepcopy

import numpy as np

class SpColor:

    def sp_colour_main(self, press_att):

        drawable_children = self.svg.xpath('//svg:path | //svg:circle | //svg:ellipse | //svg:line | //svg:polygon | //svg:polyline | //svg:rect')

        element_style_dict = SpColor.make_style_dict(self, drawable_children)

        for element in drawable_children:
            element_id = element.get_id()
            if element_id in element_style_dict:
                style_entry = element_style_dict[element_id]

                if press_att in style_entry:

                    press_att_entry = style_entry[press_att]

                    # lets pop gradients/patterns and none fills from dict
                    if 'url' in press_att_entry or 'none' in press_att_entry:
                    # if 'none' in fill:
                        element_style_dict.pop(element_id)
                        inkex.errormsg('found url or hash')
                        continue

                    parsed_fill = inkex.Color.parse_str(press_att_entry)[1]

                    # This is a workaround, because objects
                    # Which already have rgb fills
                    # End up as quoted components

                    if 'rgb' in press_att_entry:
                        parsed_fill = tuple([int(x) for x in parsed_fill])

                    element_style_dict[element_id]['rgb_tuple'] = parsed_fill

                    # inkex.errormsg(parsed_fill)

                    fill_rgb_tuple = parsed_fill # Sometimes parsed fill returns a list ?
                    element_style_dict[element_id]['rgb_tuple'] = fill_rgb_tuple
                else:
                    # This would apply when element has no fill in class/inline style/attribute
                    element_style_dict[element_id]['rgb_tuple'] = (0, 0, 0)



        if self.options.color_thres_radio == 'color_limit':

            rgb2 = (self.options.red_single_value_int, self.options.green_single_value_int, self.options.blue_single_value_int)

            id_list = []
            color_limit_dict = {}

            for element_id in element_style_dict.keys():
                current_color = element_style_dict[element_id]['rgb_tuple']
                # inkex.errormsg(current_color)
                try:
                    thres_bool = SpColor.filter_by_component(self, current_color, rgb2)
                    if thres_bool:
                        color_limit_dict[element_id] = {}
                        color_limit_dict[element_id]['rgba_tuple'] = element_style_dict[element_id]['rgb_tuple']
                except:
                    pass
            new_color_dict = {k: v for (k, v) in element_style_dict.items() if k in color_limit_dict.keys()}

        # if self.options.draw_swatches_bool:
        #     create_palette_squares(self, new_color_dict, 'none', self.options.swatch_size_float, self.options.swatch_row_length_int)


        elif self.options.color_thres_radio == 'color_range':
            new_color_dict = SpColor.filter_by_component_ranges(self, element_style_dict)

        elif self.options.color_thres_radio == 'color_distance':

            eu_base_color = self.options.eu_base_color_inkex_color

            eu_base_color_rgb = (eu_base_color.red, eu_base_color.green, eu_base_color.blue)

            # inkex.errormsg(eu_base_color_rgb)

            # sys.exit()

            new_color_dict = SpColor.filter_by_euclidean_distances(self, element_style_dict, eu_base_color_rgb)

        id_list = []
        for object_id in new_color_dict.keys():
            id_list.append(object_id)

        final_object_list = [self.svg.getElementById(x) for x in id_list]

        # if self.options.draw_swatches_bool:
        #
        #     SpColor.create_palette_squares(self, new_color_dict, 'none', self.options.swatch_size_float, self.options.swatch_row_length_int)

        return final_object_list

    def colorsys_order_list(self, color_list, color_space):

        import colorsys

        if color_space == 'hsv':
            color_list.sort(key=lambda rgb: colorsys.rgb_to_hsv(*rgb))
        if color_space == 'hls':
            color_list.sort(key=lambda rgb: colorsys.rgb_to_hls(*rgb))


    def threshold_bool(self, value, lower_thres, upper_thres):
        if (lower_thres <= value <= upper_thres):
            return True
        else:
            return False

    def make_style_dict(self, element_list):

        element_style_dict = {}


        for element in element_list:
            element_id = element.get_id()
            element_style_dict[element_id] = {}
            element_composed_style = element.specified_style()

            for style_key in element_composed_style.keys():
                element_style_dict[element_id][style_key] = element_composed_style[style_key]

        return element_style_dict

    def rect_path(self, x, y, width, height, fill_color, stroke_color='black'):
        x0 = x
        y0 = y
        x1 = x0 + width
        y1 = y0 + height

        # Build path box string
        d = f'M {x0} {y0} {x0} {y1} {x1} {y1} {x1} {y0} z'
        # inkex.errormsg(d)

        my_path = PathElement()
        my_path.set('d', d)
        my_path.style['stroke'] = stroke_color
        my_path.style['stroke-width'] = (width / 100) * 5
        # inkex.errormsg(fill_color)
        my_path.style['fill'] = fill_color
        # my_path.style['fill'] = 'red'

        return my_path


    def create_palette_squares(self, color_dict, layer_name, swatch_size, row_length):
        parent = self.svg
        palette_layer = Layer()

        palette_name = getattr(self.options, 'palette_name', 'Web_Safe')

        palette_layer_id = 'palette_squares_' + str(time.time()).replace('.', '')
        label = palette_name + '_' + str(time.time()).replace('.', '')
        palette_layer.set('inkscape:label', label)
        palette_layer.set('id', palette_layer_id)

        # total_dict_len = len(color_dict.keys())
        # y_shift_factor = int(total_dict_len / 40)

        color_list = []

        for entry in color_dict.values():

            try:
                # entry_color = f'rgb{entry["rgb_tuple"]}'
                entry_color = entry["rgb_tuple"]
            except:
                continue

            if entry_color not in color_list:
                color_list.append(entry_color)
            else:
                continue

        # Now lets use numpy to colour distance sort color_list !

        # np_euclidean_list = sort_color_list_by_numpy_distance(self, color_list, base_color=(255, 255, 255))
        # color_list = [f'rgb({x[1][0]}, {x[1][1]}, {x[1][2]})' for x in np_euclidean_list]

        # colorsys_order_list(self, color_list, color_space='hls')
        # color_list = [f'rgb({x[0]}, {x[1]}, {x[2]})' for x in color_list]

        np_euclidean_list = SpColor.sort_color_list_by_distance(self, color_list, base_color=(255, 255, 255))
        color_list = [f'rgb({x[1][0]}, {x[1][1]}, {x[1][2]})' for x in np_euclidean_list]

        # inkex.errormsg(color_list)
        #
        # sys.exit()


        entry_x = 0
        shift_y = ((math.floor(len(color_dict.values()) / row_length)) * swatch_size) + swatch_size
        entry_count = 0
        shift_x = 0

        for entry_color in color_list:

            entry_y = (math.floor(entry_count / row_length) * swatch_size) - shift_y
            entry_x = (entry_count * swatch_size) - shift_x

            entry_rect = SpColor.rect_path(self, entry_x, entry_y, swatch_size, swatch_size, entry_color)
            palette_layer.append(entry_rect)
            entry_x += swatch_size
            entry_x = entry_x - shift_x
            entry_count += 1
            shift_x = int(entry_count / row_length) * (swatch_size * row_length)

        # inkex.errormsg(color_list)

        parent.append(palette_layer)


    def filter_by_component(self, rgb1, rgb2):

        r_bool = self.options.red_single_value_bool
        g_bool = self.options.green_single_value_bool
        b_bool = self.options.blue_single_value_bool

        # First build a set of comparison lists.
        r1 = rgb1[0]
        g1 = rgb1[1]
        b1 = rgb1[2]

        r2 = rgb2[0]
        g2 = rgb2[1]
        b2 = rgb2[2]

        component_bool_list = []
        # Compare each component
        if self.options.red_single_value_bool:
            if self.options.red_single_value_more_than_bool:
                red_bool = r1 >= r2
                component_bool_list.append(red_bool)
            else:
                red_bool = r1 <= r2
                component_bool_list.append(red_bool)

        if self.options.green_single_value_bool:
            if self.options.green_single_value_more_than_bool:
                green_bool = g1 >= g2
                component_bool_list.append(green_bool)
            else:
                green_bool = g1 <= g2
                component_bool_list.append(green_bool)

        if self.options.blue_single_value_bool:
            if self.options.blue_single_value_more_than_bool:
                blue_bool = b1 >= b2
                component_bool_list.append(blue_bool)
            else:
                blue_bool = b1 <= b2
                component_bool_list.append(blue_bool)

        # inkex.errormsg(component_bool_list)

        if False in component_bool_list:
            return False
        else:
            return True


    def filter_by_component_ranges(self, element_style_dict):

        red_lower = self.options.red_color_range_lower_int
        red_upper = self.options.red_color_range_upper_int

        green_lower = self.options.green_color_range_lower_int
        green_upper = self.options.green_color_range_upper_int

        blue_lower = self.options.blue_color_range_lower_int
        blue_upper = self.options.blue_color_range_upper_int

        current_element_style_dict = deepcopy(element_style_dict)

        if self.options.red_color_range_bool:
            red_range_dict = SpColor.filter_by_component_range(self, element_style_dict, red_lower, red_upper)
            current_element_style_dict = {k: v for (k, v) in current_element_style_dict.items() if k in red_range_dict.keys()}

        if self.options.green_color_range_bool:
            green_range_dict = SpColor.filter_by_component_range(self, element_style_dict, green_lower, green_upper)
            current_element_style_dict = {k: v for (k, v) in current_element_style_dict.items() if k in green_range_dict.keys()}

        if self.options.blue_color_range_bool:
            blue_range_dict = SpColor.filter_by_component_range(self, element_style_dict, blue_lower, blue_upper)
            current_element_style_dict = {k: v for (k, v) in current_element_style_dict.items() if k in blue_range_dict.keys()}

        # inkex.errormsg(current_element_style_dict)
        return current_element_style_dict

    def filter_by_component_range(self, element_style_dict, lower_thres, upper_thres):
        # Test if the colour value is in the range:

        component_range_dict = {}

        for element_id in element_style_dict.keys():
            current_color = element_style_dict[element_id]['rgb_tuple']
            current_color_bool = SpColor.threshold_bool(self, current_color[0], lower_thres, upper_thres)
            if current_color_bool:
                component_range_dict[element_id] = {}
                component_range_dict[element_id]['rgb_tuple'] = current_color
                component_range_dict[element_id]['rgba'] = current_color
        # inkex.errormsg(component_range_dict)
        return component_range_dict

    def filter_by_euclidean_distances(self, element_style_dict, eu_base_color_rgb):

        if self.options.euclidean_weighting_radio != 'custom':
            weight_tuple = self.options.euclidean_weighting_radio.split('_')
            weight_tuple = [int(x) for x in weight_tuple]
        else:
            weight_tuple = (self.options.r_weight_int, self.options.g_weight_int, self.options.b_weight_int)

        # inkex.errormsg(weight_tuple)

        # sys.exit()

        # max_distance = 441.6729559300637
        max_distance = self.options.eu_threshold_float

        euclidean_distance_dict = {}

        for element_id in element_style_dict.keys():
            current_color = element_style_dict[element_id]['rgb_tuple']

            eu_distance = SpColor.get_euclidean_distance(self, current_color, eu_base_color_rgb, weight_tuple)

            # inkex.errormsg(eu_distance)

            current_color_bool = eu_distance < max_distance

            if current_color_bool:
                euclidean_distance_dict[element_id] = {}
                euclidean_distance_dict[element_id]['rgb_tuple'] = current_color
                euclidean_distance_dict[element_id]['rgba'] = current_color
        # inkex.errormsg(component_range_dict)
        return euclidean_distance_dict

    def make_numpy_point_array_list(self, list_of_nodes_list):

        np_arrays_list = []

        for current_list in list_of_nodes_list:
            np_array = np.array(current_list)
            np_arrays_list.append(np_array)

        return np_arrays_list

    def sort_color_list_by_numpy_distance(self, color_list, base_color):

        numpy_array = SpColor.make_numpy_point_array_list(self, color_list)

        np_euclidean_list = SpColor.make_euclidian_point_list(self, numpy_array, base_color)

        return np_euclidean_list

    def make_euclidian_point_list(self, np_array, base_color):

        eu_points_list = []

        for point in np_array:

            eu_distance = np.linalg.norm(base_color - point)
            eu_points_list.append([eu_distance, list(point)])
        # Lets then sort by the distances we have obtained.
        from operator import itemgetter
        return sorted(eu_points_list, key=itemgetter(0))

    def sort_color_list_by_distance(self, color_list, base_color):

        eu_points_list = []

        weight_tuple = (1, 1, 1)

        for color_point in color_list:
            eu_distance = SpColor.get_euclidean_distance(self, base_color, color_point, weight_tuple)
            eu_points_list.append([eu_distance, list(color_point)])
        from operator import itemgetter
        return sorted(eu_points_list, key=itemgetter(0))

    def get_euclidean_distance(self, rgb1, rgb2, weight_tuple):

        r_weight, g_weight, b_weight = weight_tuple

        rgb1 = [int(i) for i in rgb1]
        rgb2 = [int(i) for i in rgb2]

        distance = math.sqrt(((rgb2[0] - rgb1[0])*r_weight) ** 2 +
                             ((rgb2[1] - rgb1[1])*g_weight) ** 2 +
                             ((rgb2[2] - rgb1[2])*b_weight) ** 2)

        return distance
