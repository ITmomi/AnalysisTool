import psycopg2 as pg2
import psycopg2.extras


class Connect:

    connect = None
    cursor = None

    def __init__(self, config, column=False):
        if config is None or 'host' not in config or 'port' not in config or config['host'] == '' or config['port'] == 0:
            raise RuntimeError('Connect() invalid config')
        self.config = config
        self.column = column

    def __enter__(self):
        self.connect = pg2.connect(**self.config)
        if self.connect is not None:
            self.cursor = self.connect.cursor()
            if self.column:
                self.cursor = self.connect.cursor(cursor_factory=psycopg2.extras.DictCursor)
            else:
                self.cursor = self.connect.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connect.commit()
        self.cursor.close()
        self.connect.close()
