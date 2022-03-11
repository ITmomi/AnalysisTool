from resource.script.preprocess_base import PreprocessBase


class PreprocessScript(PreprocessBase):
    """
    .. class:: PreprocessScript

        This class is for preprocessing input file by user script.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self) -> list:
        """
        This method will be called by sub process(convert process). Fix this method as you want.

        :return: List of String
        """
        lines = self.readlines()

        ret_lines = list()

        replace_list = ['2427A_', '2427B_', '2427C_', '2427D_', '2427E_', '2427F_']

        for line in lines:
            for replace in replace_list:
                line = line.replace(replace, '')
            ret_lines.append(line)

        return ret_lines
