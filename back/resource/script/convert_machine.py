from resource.script.convert_base import ConvertBase

import pandas as pd


class ConvertScript(ConvertBase):
    """
    .. class:: ConvertScript

        This class is for converting input file by user script.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self) -> pd.DataFrame:
        """
        This method will be called by sub process(convert process). Fix this method as you want.

        :return: DataFrame
        """

        result_list = list()

        # Read Log File
        lines = self.readlines()

        for line in lines:
            linelog = line.strip().split(',')

            if len(linelog) == 2:
                result_list.append({'key': linelog[0], 'val': linelog[1]})

        df = pd.DataFrame(result_list)

        return df
