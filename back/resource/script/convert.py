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

        # Read Log File
        lines = self.readlines()

        # Get Rules
        rules = self.get_rules()

        df = self.execute_system_converter()

        if 'device' not in df.columns:
            df['device'] = 'FIXED_DEVICE'

        return df
