import inkex


class SpBbox:

    thres_bbox_width_id_list = []
    thres_bbox_height_id_list = []
    thres_bbox_diagonal_id_list = []
    thres_bbox_area_id_list = []
    thres_bbox_ratio_width_height_id_list = []
    thres_bbox_ratio_height_width_id_list = []

    # ilist = initial list of elements
    # lets also attach a thres flag to each element (in case we need it)

    def chain_thres(self, ilist):

        # For the moment, lets ignore text elements
        for item in ilist:
            inkex.errormsg(item.TAG)
            if item.TAG.lower() == 'text' or item.TAG.lower() == 'tspan':
                ilist.remove(item)

        ilist_id_list = [x.get_id() for x in ilist]

        bbox_chained_thres_list = []

        # Height Threshold
        if self.options.bbox_width_bool:
            for element in ilist:
                if SpBbox.thres_bbox_width(self, element, self.options.bbox_width_lower, self.options.bbox_width_upper):
                    element.thres = True
                    SpBbox.thres_bbox_width_id_list.append(element.get_id())
        # Width Threshold
        if self.options.bbox_height_bool:
            for element in ilist:
                if SpBbox.thres_bbox_height(self, element, self.options.bbox_height_lower, self.options.bbox_height_upper):
                    element.thres = True
                    SpBbox.thres_bbox_height_id_list.append(element.get_id())
        # Diagonal Threshold
        if self.options.bbox_diagonal_bool:
            for element in ilist:
                if SpBbox.thres_bbox_diagonal(self, element, self.options.bbox_diagonal_lower, self.options.bbox_diagonal_upper):
                    element.thres = True
                    SpBbox.thres_bbox_diagonal_id_list.append(element.get_id())
        # Area Threshold
        if self.options.bbox_area_bool:
            for element in ilist:
                if SpBbox.thres_bbox_area(self, element, self.options.bbox_area_lower, self.options.bbox_area_upper):
                    element.thres = True
                    SpBbox.thres_bbox_area_id_list.append(element.get_id())
        # Width Height Ratio Threshold
        if self.options.bbox_ratio_width_height_bool:
            for element in ilist:
                if SpBbox.thres_bbox_ratio_width_height(self, element, self.options.bbox_ratio_width_height_lower, self.options.bbox_ratio_width_height_upper):
                    element.thres = True
                    SpBbox.thres_bbox_ratio_width_height_id_list.append(element.get_id())
        # Height Width Ratio Threshold
        if self.options.bbox_ratio_height_width_bool:
            for element in ilist:
                if SpBbox.thres_bbox_ratio_height_width(self, element, self.options.bbox_ratio_height_width_lower, self.options.bbox_ratio_height_width_upper):
                    element.thres = True
                    SpBbox.thres_bbox_ratio_height_width_id_list.append(element.get_id())

        # Lets subtract all non matched elements from master id list

        bbox_chained_thres_id_list = set(ilist_id_list) \
                                  - set(SpBbox.thres_bbox_width_id_list)\
                                  - set(SpBbox.thres_bbox_height_id_list)\
                                  - set(SpBbox.thres_bbox_diagonal_id_list)\
                                  - set(SpBbox.thres_bbox_area_id_list)\
                                  - set(SpBbox.thres_bbox_ratio_width_height_id_list)\
                                  - set(SpBbox.thres_bbox_ratio_height_width_id_list)

        return bbox_chained_thres_id_list


    def thres_bbox_width(self, element, lower_thres, upper_thres):

        bbox = element.bounding_box(True)
        width = bbox.width

        # inkex.errormsg(type(width))
        # inkex.errormsg(f'{element.get_id()} within threshold - lower: {lower_thres} upper: {upper_thres} element_value: {width}')

        if not (lower_thres < width < upper_thres):
            return True
        else:
            return False

    def thres_bbox_height(self, element, lower_thres, upper_thres):

        bbox = element.bounding_box(True)
        height = bbox.height

        if not lower_thres < height < upper_thres:
            return True
        else:
            return False

    def thres_bbox_diagonal(self, element, lower_thres, upper_thres):

        import math
        bbox = element.bounding_box(True)
        diagonal = round(math.sqrt((bbox.width**2) + (bbox.height**2)), 4)

        if not lower_thres < diagonal < upper_thres:
            # inkex.errormsg(f'{element.get_id()} within threshold - lower: {lower_thres} uppper: {upper_thres} element_value: {diagonal}')
            return True
        else:
            return False

    def thres_bbox_area(self, element, lower_thres, upper_thres):

        bbox = element.bounding_box(True)
        area = bbox.width * bbox.height

        inkex.errormsg(f'{element.get_id()} within threshold - lower: {lower_thres} upper: {upper_thres} element_value: {area}')

        if not lower_thres < area < upper_thres:
            return True
        else:
            return False

    def thres_bbox_ratio_width_height(self, element, lower_thres, upper_thres):

        bbox = element.bounding_box(True)
        width = bbox.width
        height = bbox.height
        width_height_ratio = width / height

        inkex.errormsg(f'{element.get_id()} within threshold - lower: {lower_thres} upper: {upper_thres} element_value: {width_height_ratio}')

        if not lower_thres < width_height_ratio < upper_thres:
            return True
        else:
            return False

    def thres_bbox_ratio_height_width(self, element, lower_thres, upper_thres):

        bbox = element.bounding_box(True)
        width = bbox.width
        height = bbox.height
        height_width_ratio = height / width

        inkex.errormsg(f'{element.get_id()} within threshold - lower: {lower_thres} upper: {upper_thres} element_value: {height_width_ratio}')

        if not lower_thres < height_width_ratio < upper_thres:
            return True
        else:
            return False