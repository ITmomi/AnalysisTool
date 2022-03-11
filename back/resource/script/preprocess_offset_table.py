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

        for line in lines:
            if '\"' in line:
                line = line.replace('\"', '')
            ret_lines.append(line)

        return ret_lines
