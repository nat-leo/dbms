# Test File for Engine folder
import os
from dbms.engine import engine

###############################################################################
# engine/engine.py
###############################################################################

# New users should have everything clear except a folder of the same name as the user
def new_user_database_engine_test():
    e = engine.DatabaseEngine("test")
    assert os.path.isdir(e.directory), "New user 'test' did not create a new directory"
