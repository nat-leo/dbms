import os
import pytest
import engine 

@pytest.fixture
def e(tmpdir):
    e = engine.DatabaseEngine(tmpdir)
    return e

def test_create_db(e):
    e.create_db("db1")
    assert os.path.isdir(e.directory+"/db1"), "Folder not created for database."

def test_drop_db(e):
    e.create_db("db1")
    e.drop_db("db1")
    assert os.path.isdir(e.directory+"/db1"), "Folder not created for database."

def test_create_table(e):
    e.create_db("db")
    e.create_table("db", "table")
    assert os.path.exists(e.directory+"/db/table.bin"), "File not created for table."

