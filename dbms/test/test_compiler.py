# Test File for Engine folder
import os
import pytest
from compiler import parse

# set up the compiler
@pytest.fixture
def parser():
    return parse.Parser()

# CREATE TABLE
def test_create_table(parser):
    parser.parse("CREATE TABLE table (column1: varchar(255))")
    assert parser.query_plan["operation"] == "CREATE"