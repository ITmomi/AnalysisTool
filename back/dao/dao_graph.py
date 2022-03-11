from dao.dao_base import DAOBaseClass


class DAOGraph(DAOBaseClass):
    TABLE_NAME = 'graph.function_graph_type'

    def __init__(self):
        super().__init__(table_name=DAOGraph.TABLE_NAME)

    def __del__(self):
        super().__del__()
        print('__del__', __class__)
