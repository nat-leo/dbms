# Test File for dbms/compiler
import unittest
import json
from compiler import parse

QUERIES = [
    "SELECT * FROM table",
    "SELECT col1 FROM table",
    "SELECT col1, col2, col3, col4, col5 FROM table",
    "CREATE TABLE table ( col1 varchar(255) )",
    "CREATE TABLE table ( col1 varchar(255), col2 varchar(255), col3 varchar(255) )",
]

class CompilerTest(unittest.TestCase):
    def setUp(self):
        self.sql = parse.Parser()
    
    def tearDown(self):
        pass
    
    # run the query. Checks that the string is 1. Parseable, and 2. 
    # Creates dumpable and readable (by robots) JSON.
    def is_valid_query(self, sql_query):
        self.sql.parse(sql_query)
        try:
            self.validate_json(self.sql.query_plan)
        except Exception as e:
            raise ValueError(f"json {self.sql.query_plan} failed to be validated.\n {e}")
    
    # helper for is_valid_query. Validate that the parser produces 
    # properly formatted json.
    def validate_json(self, query_plan):
        #json_str = json.dumps(query_plan) 
        #json.loads(json_str)
        
        try:   
            json_str = json.dumps(query_plan)  
        except Exception as e:
            raise ValueError(f"In Compiler Test: json.dumps() failed to convert this json into string: {query_plan}:\n {e}")
        try:         
            json.loads(json_str)
        except Exception as e:
            raise ValueError(f"In Compiler Test: json.loads() failed to parse this string into json: {json_str}:\n {e}")
        
    # test all the queries above.
    def test_sql(self):
        for query in QUERIES:
            self.is_valid_query(query)
