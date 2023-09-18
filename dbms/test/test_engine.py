# Test File for dbms/engine
import os
import shutil
import unittest
from engine import engine

###############################################################################
# engine/engine.py
###############################################################################
class EngineTest(unittest.TestCase):
    def setUp(self):
        self.eng = engine.DatabaseEngine("test", "password")

    def tearDown(self):
        shutil.rmtree(self.eng.directory)

    def test_works(self):
        print("hoorah.")
