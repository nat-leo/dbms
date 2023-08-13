import os
import logging

class Table:
    def __init__(self, name, columns: dict) -> None:
        self.name = name
        self.columns = columns
        self.row_size = sum(columns.values())

class Database:
    def __init__(self, name) -> None:
        self.name = name
        self.tables = {} # dict so we have constant access time.

    def add_table(self, table: Table):
        self.tables[table.name] = table
        logging.info(f"registered table {table.name} into database obejct {self.name}.")
    
    def remove_table(self, table: Table):
        if table.name in self.tables:
            del self.tables[table.name]
        else:
            logging.warning(f"table {table.name} was not registered in it's database object. Table file {table.name}.bin may still exist in the db directory.")

class DatabaseEngine:
    # stores all databases.
    def __init__(self) -> None:
        self.directory = os.path.join(os.path.dirname(__file__), "db") # create 'db' folder in the same dir as this file!
        self.databases = {} # dict for constant access time 
        os.mkdir(self.directory) # folder 'db' persists when program ends.

    ''' Given a set of instructions as a list, execute each
    operation from the first element to the last element.

    Elements all have one "operation" and one "child" operation:
    {
        "operation": ,
        "columns": [],
        "source": {
            "operation": "SCAN",
            "table": ,
        }
        "condition": {
            "column": ,
            "operator": ,
            "value": ,
        }
    }
    '''
    def execute(self, lqp: dict) -> list:
        # use lqp["source"]["table"] to open a connection to the file table.bin.
        # for each row in the table assert lqp["condition"]. If true, add to our list.
        # for each row in list, use lqp["columns"] to select all columns requested, and
        #add to a different list.
        #return the different list.
        return []

    # run an index scan on the table. Condition is either exactly the json from the 
    # lqp["condition"] or None.
    def scan(self, db, table, condition) -> list:
        with open(f"{db.name}/{table.name}.bin", "rb") as file:
            while True:
                rows = file.read(table.bytes_per_row)
                if not rows:
                    break
        return rows
    
    # create a table as a .bin file of the form table_name.bin
    def create_table(self, db_name: str, table_name: str, schema: dict):
        # create the table as a file
        path = f"{self.directory}/{db_name}/{table_name}.bin"
        open(path, "wb")
        
        # register the table in the right db
        table = Table(table_name, schema)
        self.databases[db_name].add_table(table)

        logging.info(f"DatabaseEngine: created Table Object {path}")

    # create a database as a directory, where the directory/folder name is db_name
    def create_db(self, db_name: str):
        # write the directory
        path = os.path.join(self.directory, db_name)
        os.mkdir(path)
        # register a db object so we can keep track of dbs and tables easier.
        db = Database(db_name)
        self.databases[db_name] = db
    
        logging.info(f"DatabaseEngine: created Database object {path}")
    
    # completely delete the table from the database
    def drop_table(self, db_name: str, table_name: str):
        # remove the object
        if db_name in self.databases:
            db = self.databases[db_name].tables
            if table_name in db:
                del db[table_name]
            else:
                logging.warning(f"DatabaseEngine: table {table_name} was not found in {db_name}. Table file {table_name}.bin may still exist in the db directory.")
        else:
            logging.warning(f"DatabaseEngine: db {db_name} was not registered. db folder {db_name} may still exist.")
        # remove the file
        try:
            os.remove(f"{self.directory}/{db_name}/{table_name}.bin")
        except OSError as e:
            logging.error(f"{e}: table was not removed.")
        
    # completely delete the the database
    def drop_db(self, db_name: str):
        if db_name in self.databases:
            del self.databases[db_name]
        else:
            logging.warning(f"DatabaseEngine: database {db_name} was not registered")
        try:
            os.rmdir(self.directory+"/"+db_name)
        except OSError as e:
            logging.error(f"{e}: dataabse folder was not removed.")
        

    # append data into table.bin as binary data
    def insert(self, db, table, data=[]):
        pass
