import unittest
import shutil 
import os

from compiler import parse
from engine import engine

class E2E(unittest.TestCase):
    def setUp(self):
        self.sql = parse.Parser()
        self.eng = engine.DatabaseEngine("test", "password")
        # create a table
        self.sql.parse("CREATE TABLE table ( col1 varchar(255), col2 varchar(255), col3 varchar(255) )")
        self.eng.execute(self.sql.query_plan)
        # add values to it
        self.sql.parse("INSERT INTO table (col1, col2, col3) VALUES (col, col, col)")
        self.eng.execute(self.sql.query_plan)

    def tearDown(self):
        shutil.rmtree(self.eng.directory)

    def test_create_table(self):
        self.sql.parse("CREATE TABLE table2 ( col1 varchar(255) )")
        self.eng.execute(self.sql.query_plan)
        
        # you should be able to read the schema after a table is created:
        # TODO

        # another way to verify relation was created is by seeing if it DatabaseEngine.ls() lists it.
        assert "table2" in self.eng.ls(), f"CREATE TABLE should be listable by the DatabaseEngine"

    def test_insert(self):
        self.sql.parse("INSERT INTO table (col1, col2, col3) VALUES (col, col, col)")
        self.eng.execute(self.sql.query_plan)

    def test_select(self):
        self.sql.parse("SELECT * FROM table")
        data = self.eng.execute(self.sql.query_plan)
        assert data == [{'col1': 'col', 'col2': 'col', 'col3': 'col'}], f"Incorrect data: \n {data}"

    def test_update(self):
        self.sql.parse("UPDATE table SET col1=val")
        self.eng.execute(self.sql.query_plan)
        self.sql.parse("SELECT * FROM table")
        data = self.eng.execute(self.sql.query_plan)
        assert data == [{'col1': 'val', 'col2': 'col', 'col3': 'col'}], f"Incorrect data: \n {data}"

    def test_delete(self):
        self.sql.parse("DELETE FROM table")
        self.eng.execute(self.sql.query_plan)
        self.sql.parse("SELECT * FROM table")
        data = self.eng.execute(self.sql.query_plan)
        assert data == [], f"Incorrect data: \n {data}"

