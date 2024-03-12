import os
from DataWriter.DataWriterBase import DataWriterBase
from sqlite_util import (
    create_datebase,
    select_database,
    insert_database,
)
from log_util import get_logger

logger = get_logger()


class SqliteDataWriter(DataWriterBase):
    def __init__(self, db_path, table, create_sql):
        self.db_path = db_path
        self.table = table
        if not os.path.exists(self.db_path):
            create_datebase(self.db_path, create_sql)

    def write_data(self, path, sql, data):
        logger.info(f"Writing {str(data)} to {self.db_path}")
        insert_database(self.db_path, sql, data)

    def get_data(self, sql):
        return select_database(self.db_path, sql)
