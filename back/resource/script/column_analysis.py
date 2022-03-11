from resource.script.analysis_base import AnalysisBase


class ColumnAnalysisScript(AnalysisBase):
    """
    .. class:: ColumnAnalysisScript

        This class is for analyze specific column data by user script.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self, data) -> float:
        """
        This method will be called by Main Process. Fix this method as you want.

        :param data: pandas.Series pandas.DataFrame Data
        :return: analyze result. (float)
        """

        return data.mean()
