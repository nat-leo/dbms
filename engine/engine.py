import os
import logging

class Table:
    def __init__(self, name, schema: dict) -> None:
        self.name = name
        self.schema = schema
        self.row_size = sum([value["bytes"] for key, value in self.schema.items()])
        self.total_rows = 0
        self.index_structure = {}

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
    def scan(self, db_name: str, table_name: str, condition) -> list:
        # alias the table
        t = self.databases[db_name].tables[table_name]

        # read entire file
        with open(f"{self.directory}/{db_name}/{table_name}.bin", "rb") as file:
            data = file.read()
        
        # format data into a nice list of dicts
        data_list = []
        for i in range(1, t.total_rows):
            datum = data[i-1:t.row_size*i]
            row = {}
            for key, value in t.schema.items():
                row[key] = datum[0:value['bytes']]
                datum = datum[value['bytes']:]
            data_list.append(row)

        return data_list
    
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
    def insert(self, db_name: str, table_name: str, data: list[dict]):
        try:
            t = self.databases[db_name].tables[table_name]
        except KeyError as e:
            logging.error(f'{e}: Insert not performed.')

        append_string = b''
        for element in data:
            t.total_rows += 1
            for key, value in element.items():
                total_bytes = t.schema[key]["bytes"]
                # error checking
                if type(value) != t.schema[key]["type"]:
                    logging.error(f'wrong type {type(value)} for schema element of type {t.schema[key]["type"]}')
                
                # go case-by-case for binary conversion
                if type(value) == str:
                    original_string = value.encode("utf-8")
                elif type(value) == int:
                    # using str().encode() saves on space compared to bin()
                    original_string = str(value).encode("utf-8")
                    #original_string = bin(value)
                
                # fill leftover space
                if((total_bytes - len(original_string)) < 0): # error check
                    logging.error("too much data for schema element")
                    raise ValueError(f"{value} of size {len(original_string)} too much data for schema max size of {t.schema[key]['bytes']}")
                
                fill_bytes = b'\x00' * (total_bytes - len(original_string))
                insert_string = original_string + fill_bytes

                # append the now binary value to the append string.
                append_string += insert_string

        # write every single data point in one go.
        try:
            with open(f"{self.directory}/{db_name}/{table_name}.bin", "ab") as file:
                file.write(append_string)
        except:
            logging.error(f'{e}: unable to write data to file.')