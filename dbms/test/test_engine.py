# Test File for Engine folder
import os
import pytest
from engine import engine

###############################################################################
# engine/engine.py
###############################################################################

# New user created
@pytest.fixture
def new_user():
    return engine.DatabaseEngine("test")

# New user creates table
@pytest.fixture
def creates_table(new_user):
    new_user.create_table("table", {})
    return new_user

# New users should have everything clear except a folder of the same name as the user
def test_new_user_database_engine(new_user):
    assert os.path.isdir(new_user.directory), "New user 'test' did not create a new directory"

# New users should be able to create any new table without error
def test_new_user_create_table(creates_table):
    assert os.path.exists(creates_table.directory+"/table.bin"), "New table 'table' did not create a new file"
    
# Database object should have a new table in its tables attribute when user calls create table
def test_new_user_table_in_db_object(creates_table):
    assert "table" in creates_table.tables, "New table 'table' not created in database object"
