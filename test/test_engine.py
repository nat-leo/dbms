# Test File for Engine folder
import os
import pytest
from dbms.engine import engine

###############################################################################
# engine/engine.py
###############################################################################

# New user created
@pytest.fixture
def new_user():
    return engine.DatabaseEngine("test")

# New users should have everything clear except a folder of the same name as the user
def test_new_user_database_engine(new_user):
    assert os.path.isdir(new_user.directory), "New user 'test' did not create a new directory"

# New users should be able to create any new table without error
def test_new_user_create_table(new_user):
    new_user.create_table("test", "table", {"schema": {"type": str, "bytes": 64}})
    assert os.path.exists(new_user.directory+"/table.bin"), "New table 'table' did not create a new file"