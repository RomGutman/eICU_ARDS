import psycopg2
import pandas as pd
import os


class LoadData:
    def __init__(self):
        self._username = 'postgres'
        self._db_name = 'eicu'
        self._schema_name = 'eicu_crd'
        self._sqlhost = 'localhost'
        self._sqlport = 5432
        self._con = None

    @property
    def con(self):
        """

        :return:
        """
        if self._con is not None:
            return self._con
        self._con = psycopg2.connect(dbname=self._db_name, user=self._username, host=self._sqlhost, port=self._sqlport)
        return self._con

    def query_db(self, query, params=None):
        """

        :param params:
        :param query:
        :return:
        """
        tr = pd.read_sql_query(query, self.con, params=params)
        df = tr.copy()

