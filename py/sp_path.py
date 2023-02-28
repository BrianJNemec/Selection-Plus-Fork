import inkex


class SpPath:

    thres_node_count_id_list = []

    # Just leave path letter commands
    def return_alphabet_string_only(self, my_string):
        import re
        regex = re.compile('[^a-zA-Z]')
        alphabet_string = regex.sub('', my_string)
        return(alphabet_string)

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

        combined_path_bool = d.lower().count('m') > 1

        # Return the path type and if the path is combined from multiple paths
        return path_type, combined_path_bool

    def paths_thres_node_count(self, paths):

        lower_thres = self.options.node_count_lower
        upper_thres = self.options.node_count_upper

        paths_id_list = [x.get_id() for x in paths]

        for path_object in paths:
            if SpPath.thres_node_count(self, path_object, lower_thres, upper_thres):
                SpPath.thres_node_count_id_list.append(path_object.get_id())

        return set(paths_id_list) - set(SpPath.thres_node_count_id_list)

    def thres_node_count(self, path_object, lower_thres, upper_thres):

        node_count = SpPath.get_node_count(self, path_object)
        if not lower_thres <= node_count <= upper_thres:
            return True
        else:
            return False

    def get_node_count(self, path_object):

        # end_points is a generator
        node_count = 0
        for node in path_object.path.end_points:
            node_count += 1

        return node_count

