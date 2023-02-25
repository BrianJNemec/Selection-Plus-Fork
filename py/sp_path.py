class SpPath:

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

        return path_type, combined_path_bool