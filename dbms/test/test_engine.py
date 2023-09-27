# Test File for dbms/engine
import os
import shutil
import unittest
from engine import engine
from compiler import parse

###############################################################################
# engine/engine.py
###############################################################################
class EngineTest(unittest.TestCase):
    def setUp(self):
        self.sql = parse.Parser()
        self.eng = engine.DatabaseEngine("test", "password")

    def tearDown(self):
        shutil.rmtree(self.eng.directory)

    def test_fill_index_structure(self):
        self.sql.parse("CREATE TABLE table (key varchar(255))") # if parse returns a query plan, we can make this a one liner.
        self.eng.execute(self.sql.query_plan) # if parse returns a query plan, we can make this a one liner with the line above.
        data = ["alice", "zicra", "bob", "monument", "kiki"]
        for word in data:
            self.sql.parse(f"INSERT INTO table (key) VALUES ({word})")
            self.eng.execute(self.sql.query_plan)
        
        read_data = self.eng.table_scan("table")
        read_data = [row["key"] for row in read_data]

class TableTest(unittest.TestCase):
    def setUp(self) -> None:
        self.sql = parse.Parser()
        self.eng = engine.DatabaseEngine("test", "password")
        
        # Fill a table with some values
        self.sql.parse("CREATE TABLE table (key varchar(255))") # if parse returns a query plan, we can make this a one liner.
        self.eng.execute(self.sql.query_plan) # if parse returns a query plan, we can make this a one liner with the line above.
        data = ["alice", "zicra", "bob", "monument", "kiki"]
        for word in data:
            self.sql.parse(f"INSERT INTO table (key) VALUES ({word})")
            self.eng.execute(self.sql.query_plan)

    def tearDown(self):
        shutil.rmtree(self.eng.directory)

    def test_if_index_structure_is_initialized(self):
        table = self.eng.tables[self.eng.ls()[0]] # get the first table listed
        assert isinstance(table, engine.Table), f"{table} is not a Table Object."

        # act
        self.sql.parse("SELECT * FROM table") # MAKE PARSE RETURN THE QUERY PLAN!!!!!!! Digging the hole a little deeper over here );
        data = self.eng.execute(self.sql.query_plan)
        # assert
        index = table.index_structure # this is a dict of lists
        for row in data:
            assert index.search(row["key"]) is not None # HARDCODED