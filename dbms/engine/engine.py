import os
import json
import logging
import hashlib

from . import hashmap

# Table Class
# Used by Database Object. Table objects are created to represent tables (duh) which themselves are directories. 
# Each table gets its own file. Only that file will contain data associated with the table on-disk.
class Table:
    def __init__(self, name, schema: dict) -> None:
        self.name = name # name of the table & corresponding file.
        self.schema = schema # keep track of the type and size (in bytes \x00) of columns.
        self.row_size = sum([int(value["bytes"]) for key, value in self.schema.items()]) # total size of each row in bytes. Useful for seeking data in files.
        self.total_rows = 0 # keep track of the size of the table
        # if a database can hold many tables, then each table should control their own index structure.
        # This also means that the tables themselves should do index scans. 
        # But, should a table also control writing to and from files?
        self.index_structure = hashmap.Hashmap()
        self.init_index_structure()

    # fill the index structure of the table. Data should be the entire relation, rows are read 
    # in order. Key is which column in the schema we're building the index structure with. It must be 
    # part of the schema.
    def init_index_structure(self, data, key):
        # make sure the key is in rows, just use the first row.
        if key not in self.schema:
            raise KeyError(f"key {key} not part of the schema {schema}")
        
        # 'data' should contain the entire relation.
        self.total_rows = len(data)
        # insert the key value pairs into the dataset.
        for i in range(len(data)):
            self.index_structure.insert(data[key], i*self.row_size)

    def is_index_scannable(self):
        pass

    def search(self):
        pass

# Database Engine class
# Currently performs file scans, delete, updates, and inserts. 
class DatabaseEngine:
    # stores all databases.
    def __init__(self, user, password=None) -> None:
        self.user = user
        self.directory = os.path.join(os.path.dirname(__file__), user) # create user folder in the same dir as this file!
        self.tables = {} # const lookup time for table objects.
        self.init_db(password) # init the database
        self.init_tables()

    def execute(self, query_plan: dict) -> list:
        table = query_plan["table"] # all require the table
        if query_plan["operation"] == "SELECT":
            condition = query_plan["condition"]
            return self.table_scan(table, condition)
        elif query_plan["operation"] == "UPDATE":
            condition = query_plan["condition"]
            set = query_plan["set"]
            return self.update(table, set, condition)
        elif query_plan["operation"] == "INSERT":
            values = query_plan["values"]
            return self.insert(table, values)
        elif query_plan["operation"] == "DELETE":
            condition = query_plan["condition"]
            return self.delete(table, condition)
        elif query_plan["operation"] == "CREATE":
            schema = query_plan["schema"]
            return self.create_table(table, schema)

    # run an index scan on the table. Condition is either exactly the json from the 
    # lqp["condition"] or None.
    def table_scan(self, table_name: str, condition = None) -> list:
        # alias the table
        if table_name not in self.tables:
            raise KeyError(f"{self.tables} is has no key called {table_name}.")
        t = self.tables[table_name]

        # read entire file
        path = os.path.join(self.directory, table_name, table_name+".bin")
        with open(path, "rb") as file:
            data = file.read()
        logging.info(f"read entire table {table_name}. Data read: {data}")

        # format data into a nice list of dicts
        data_list = []
        for i in range(t.total_rows):
            datum = data[:t.row_size]
            row = {}
            for key, attribute in t.schema.items():
                row[key] = datum[0:int(attribute['bytes'])].replace(b"\x00", b'').decode()
                datum = datum[int(attribute['bytes']):]
                logging.info(f"read {row[key]}")
            data = data[t.row_size:]
            if condition is None:
                data_list.append(row)
            else:
                cond = f'{row[condition["column"]]} {condition["operator"]} {condition["value"]}'
                logging.info(f"engine: scan: {cond}")
                logging.info(f'evaluates to {eval(cond)}')
                if eval(cond):
                    data_list.append(row)
        return data_list
    
    # append data into table.bin as binary data
    def insert(self, table_name: str, data: list, write_type="a"):
        t = self.tables[table_name]
        # write the data to one string, and append the entire string
        t.total_rows += len(data)
        append_string = b''
        for row in data:
            for i in range(len(row)):
                attributes = list(t.schema.values())
                # do a type check, get the maximum bytes a column can hold, 
                # and convert the data to a binary string.
                #if type(row[i]) != attributes[i]["type"]:
                #    logging.error(f'wrong type {type(row[i])} for schema element of type {attributes[i]["type"]}')
                total_bytes = int(attributes[i]["bytes"])
                original_string = str(row[i]).encode("utf-8")

                # fill leftover space with a \x00.
                if((total_bytes - len(original_string)) < 0): # error check
                    logging.error("too much data for schema element")
                    raise ValueError(f"{row[i]} of size {len(original_string)} too much data for schema max size of {t.schema[key]['bytes']}")
                fill_bytes = b'\x00' * (total_bytes - len(original_string))
                insert_string = original_string + fill_bytes

                append_string += insert_string

        # once all the data is on one binary string,
        # append the data to the file
        try:
            path = os.path.join(self.directory, table_name, table_name+".bin")
            with open(path, write_type+"b") as file:
                file.write(append_string)
        except:
            logging.error(f'{e}: unable to write data to file.')

    def update(self, table_name: str, set: list[dict], condition = None):
        table = self.tables[table_name]
        data = self.table_scan(table_name, None)
        logging.info(f'table: {table.schema}')
        # after we grabbed ALL the data, only update the rows that match the condition.
        #otherwise, we have to go through the database and figure out where all our data is and remove it.
        #so overwriting right not is just a little easier to do. Definitely need to make this faster in the future.
        for row in data:
            if condition is None:
                for set_column in set:
                    row[set_column["column"]] = set_column["value"]
                logging.info(f"engine: update: Updated {set} for {row}.")
            else:
                cond = f'{row[condition["column"]]} {condition["operator"]} {condition["value"]}'
                if eval(cond):
                    for update in set:
                        row[update["column"]] = update["value"]
                    logging.info(f"engine: update with condition: Updated {set} for {row}.")
                    
        table.total_rows = 0
        insert_list = []
        for row in data:
            row_list = []
            for key, value in row.items():
                conversions = {'varchar': str}
                t = conversions[table.schema[key]['type']]
                row_list.append(t(value))
            insert_list.append(row_list)

        #insert_list = [[table.schema[key]["type"](value) for key, value in row.items()] for row in data]
        logging.info(f'engine: update: inserting {insert_list}')
        self.insert(table_name, insert_list, 'w') # this insert overwrites the entire database. 
    
    def delete(self, table_name: str, condition = None):
        t = self.tables[table_name]
        data = self.table_scan(table_name, condition)
        
        filtered_list = []
        if condition:
            for datum in data:
                cond = f'{datum[condition["column"]]} {condition["operator"]} {condition["value"]}'
                if eval(cond):
                    # t.total_rows -= 1
                    # t.index_structure.remove(datum)
                    continue
                else:
                    filtered_list.append(datum)
        else:
            t.total_rows = 0
            t.index_structure = {}

        t.total_rows = 0
        self.insert(table_name, filtered_list, "w")
    
    # create a table as a .bin file of the form table_name.bin
    def create_table(self, table_name: str, schema: dict):
        # create the table as a file
        table_dir = os.path.join(self.directory, table_name)
        os.mkdir(table_dir)
        # paths
        data_path = os.path.join(table_dir, table_name+".bin")
        schema_path = os.path.join(table_dir, "schema.json")
        # init an empty file b/c it's nice to see it before first append.
        open(data_path, "wb")
        # save the schema
        with open(schema_path, "w") as file:
            json.dump(schema, file)
        
        # register the table in the right db
        table = Table(table_name, schema)
        self.tables[table_name] = table

        logging.info(f"DatabaseEngine: created Table Object {data_path}")

    # We're keeping track of table objects so later we can give each
    #table it's own index structure. 
    def init_tables(self):
        tables = self.ls()
        for table_name in tables:
            schema = self.get_schema(table_name)
            t = Table(table_name, schema)
            self.tables[table_name] = t
            # This stuff must occur AFTER self.tables has the table_name in the DatabaseEngine object
            #because table_scan checks and throws errors on table_names that aren't in self.tables yet!
            data = self.table_scan(table_name)
            t.total_rows = len(data) 
            if t.total_rows != self.tables[table_name].total_rows:
                raise ValueError("You suck")

    # helper for init tables. We need to read the schema from the table directory 
    #so we can populate our database engine with Table Objects.
    def get_schema(self, table_name):
        path = os.path.join(self.directory, table_name, "schema.json")
        with open(path, "r") as file:
            schema = json.loads(file.read())
        return schema

    # check if database exists, if it does, login, else
    #create the database
    def init_db(self, password):
        if os.path.exists(self.directory):
            self.login(password)
        else:
            self.create_db(password)
    
    # helper function used when the engine is initialized. This creates a directory of 
    # the name self.user. The next form of this should be "init_db" so that users that aren't
    # new can have access to their previous user directory.
    def create_db(self, password):
        if os.path.exists(self.directory):
            logging.info("Directory already exists for user. Welcome back.")
        else:
            try:
                os.mkdir(self.directory)
                # salt and hash the password (hash+salt is 1024 bytes)
                size = 1024
                password_length = len(password)
                salt = os.urandom(size-password_length)
                hashed = hashlib.sha256(password.encode('utf-8')+salt).hexdigest()
                # store the hashed password and salt in separate files. Otherwise,
                #we'd have to convert the hashed password to binary and it's a pain
                #in the butt (But not reallyt. This is probably a weed we'll have to 
                #pull later.)
                with open(self.directory+"/hash.txt", "w") as file:
                    file.write(hashed)
                with open(self.directory+"/salt.bin", "wb") as file:
                    file.write(salt)
                logging.info("Directory created for new user. Welcome!")
            except OSError as e:
                logging.error(f"Error creating directory: {e}")
    
    # completely delete the table from the database
    def drop_table(self, table_name: str):
        try:
            os.remove(f"{self.directory}/{table_name}.bin")
        except OSError as e:
            logging.error(f"{e}: table was not removed.")

        # only delete the table if removing the file was successful
        del self.tables[table_name]

    # helper function used when the engine is initialized. This lets users login.
    # ASSUMES: directory exists and has a file called password.txt
    def login(self, password):
        # read the password (1st line) and salt (2nd line) from file
        with open(self.directory+"/hash.txt", "r") as file:
            hashed_actual = file.read()
        with open(self.directory+"/salt.bin", "rb") as file:
            salt = file.read()
        # encrpyt the password with
        hashed_try = hashlib.sha256(password.encode('utf-8')+salt).hexdigest()
        if hashed_try != hashed_actual:
            raise ValueError("Incorrect password.")

    # list out every table located in the current directory
    #exclude files that aren't tables like password and salt.
    def ls(self):
        tables = []
        black_list = ["hash.txt", "salt.bin"]
        for file in os.listdir(self.directory):
            if file not in black_list:
                tables.append(file.split(".")[0])
        return tables

if __name__ == "__main__":
    schema = {
        "address": {"type": str, "bytes": 64}, 
        "price": {"type": int, "bytes": 5}, 
        "zip_code": {"type": str, "bytes": 5},
        "beds": {"type": int, "bytes": 2}, 
        "baths": {"type": int, "bytes": 2},
    }

    data = [
        ("123 Main St", 1500, "12345", 2, 1),
        ("456 Elm St", 2000, "23456", 3, 2),
        ("789 Oak Ave", 1800, "34567", 1, 1),
        ("101 Pine Rd", 2200, "45678", 3, 2),
        ("222 Maple Dr", 2800, "56789", 4, 3),
    ]
    logging.basicConfig(level=logging.DEBUG)
    db = DatabaseEngine("rentals")
    db.create_table("apts", schema)
    # INSERT INTO apts (address, price, zip_code, bed, bath) VALUES ('123 Main St', 1500, '12345', 2, 1), ('456 Elm St', 2000, '23456', 3, 2), etc
    d = db.execute({'operation': 'INSERT', 'columns': [], 'table': 'apts', 'values': data})
    logging.info(d)
    # SELECT * FROM apts WHERE price < 1500
    #data_list = db.execute({'operation': 'SELECT', 'columns': ['*'], 'table': 'apts', 'condition': {'column': 'price', 'operator': '<', 'value': '2000'}})
    #logging.info(f"data found: {data_list}")

    # UPDATE apts SET price = 1500
    db.execute({'operation': 'UPDATE', 'columns': ['*'], 'table': 'apts', 'set': [{'column': 'price', 'value': '1500'}], 'condition': None})
    # SELECT * FROM apts WHERE price < 1500
    #data_list = db.execute({'operation': 'SELECT', 'columns': ['*'], 'table': 'apts', 'condition': {'column': 'price', 'operator': '>', 'value': '2000'}})
    #logging.info(f"data found: {data_list}. Should be empty.")
    # DELETE * FROM apts
    db.execute({'operation': 'DELETE', 'columns': ['*'], 'table': 'apts', 'condition': None})
    # SELECT * FROM apts
    data_list = db.execute({'operation': 'SELECT', 'columns': ['*'], 'table': 'apts', 'condition': None})
    logging.info(f"data deleted: {data_list}. Should be empty.")
