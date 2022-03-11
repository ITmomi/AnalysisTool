from resource.script.analysis_base import AnalysisBase

import pandas as pd


class GenericAnalysisScript(AnalysisBase):
    """
    .. class:: GenericAnalysisScript

        This class is for analyze data by user script.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self) -> pd.DataFrame:
        """
        This method will be called by Main Process. Fix this method as you want.

        :return: DataFrame
        """
        df = self.get_df()

        ref_df = self.get_data_from_sql()

        # df['c_x_p1xr'] = df['c'] * ref_df['p1_xr'].mean()

        return df
