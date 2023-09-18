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