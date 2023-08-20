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
    def __init__(self, user) -> None:
        self.user = user
        self.directory = os.path.join(os.path.dirname(__file__), user) # create user folder in the same dir as this file!
        self.databases = {user: Database(name=user)} # dict for constant access time 
        self.create_db(self.user)

    def execute(self, query_plan: dict) -> list:
        if query_plan["operation"] == "SELECT":
            table = query_plan["table"]
            condition = query_plan["condition"]
            return self.scan(self.user, table, condition)
        elif query_plan["operation"] == "UPDATE":
            pass
        elif query_plan["operation"] == "INSERT":
            table = query_plan["table"]
            values = query_plan["values"]
            return self.insert(self.user, table, values)
        elif query_plan["operation"] == "DELETE":
            pass

    # run an index scan on the table. Condition is either exactly the json from the 
    # lqp["condition"] or None.
    def scan(self, db_name: str, table_name: str, condition = None) -> list:
        # alias the table
        if not self.databases[db_name].tables:
            raise KeyError(f"{self.databases[db_name]} is empty.")
        if not self.databases[db_name].tables[table_name]:
            raise KeyError(f"{self.databases[db_name]} is has no key called {table_name}.")
        t = self.databases[db_name].tables[table_name]

        # read entire file
        with open(f"{self.directory}/{table_name}.bin", "rb") as file:
            data = file.read()
        logging.info(f"read entire table {table_name}. Data read: {data}")
        # format data into a nice list of dicts
        data_list = []
        for i in range(t.total_rows):
            datum = data[:t.row_size]
            row = {}
            for key, value in t.schema.items():
                row[key] = datum[0:value['bytes']].replace(b"\x00", b'').decode()
                print(type(row[key]))
                datum = datum[value['bytes']:]
                print('after: ', datum)
            if condition is None:
                data_list.append(row)
            else:
                cond = f'{row[condition["column"]]} {condition["operator"]} {condition["value"]}'
                if eval(cond):
                    data_list.append(row)

        return data_list
    
    def delete(self, db_name: str, table_name: str, condition = None):
        t = self.databases[db_name].tables[table_name]
        data = self.scan(db_name, table_name, condition)
        
        filtered_list = []
        if condition:
            for datum in data:
                cond = f'{datum[condition["column"]]} {condition["operator"]} {condition["value"]}'
                if eval(cond):
                    t.total_rows -= 1
                    # t.index_structure.remove(datum)
                    continue
                else:
                    filtered_list.append(datum)
        else:
            t.total_rows = 0
            t.index_structure = {}

        self.insert(db_name, table_name, write_type="w")

    def update(self, db_name: str, table_name: str, condition = None):
        pass
    
    # create a table as a .bin file of the form table_name.bin
    def create_table(self, db_name: str, table_name: str, schema: dict):
        # create the table as a file
        path = f"{self.directory}/{table_name}.bin"
        open(path, "wb")
        
        # register the table in the right db
        table = Table(table_name, schema)
        self.databases[db_name].add_table(table)

        logging.info(f"DatabaseEngine: created Table Object {path}")

    # create a database as a directory, where the directory/folder name is db_name
    def create_db(self, db_name: str):
        if os.path.exists(self.directory):
            logging.info("Directory already exists for user. Welcome back.")
        else:
            try:
                os.mkdir(self.directory)
                logging.info("Directory created for new user. Welcome!")
            except OSError as e:
                logging.error(f"Error creating directory: {e}")
        # register a db object so we can keep track of dbs and tables easier.
        db = Database(db_name)
        self.databases[db_name] = db
    
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
            logging.error(f"{e}: database folder was not removed.")
        

    # append data into table.bin as binary data
    def insert(self, db_name: str, table_name: str, data: list, write_type="a"):
        try:
            t = self.databases[db_name].tables[table_name]
        except KeyError as e:
            logging.error(f'{e}: Insert not performed.')

        append_string = b''
        for row in data:
            t.total_rows += 1
            index = 0
            for key, value in t.schema.items():
                total_bytes = value["bytes"]
                # error checking
                if type(row[index]) != value["type"]:
                    logging.error(f'wrong type {type(row[index])} for schema element of type {t.schema[key]["type"]}')
                
                # go case-by-case for binary conversion
                if type(row[index]) == str:
                    original_string = row[index].encode("utf-8")
                elif type(row[index]) == int:
                    # using str().encode() saves on space compared to bin()
                    original_string = str(row[index]).encode("utf-8")
                    #original_string = bin(value)
                
                # fill leftover space
                if((total_bytes - len(original_string)) < 0): # error check
                    logging.error("too much data for schema element")
                    raise ValueError(f"{row[index]} of size {len(original_string)} too much data for schema max size of {t.schema[key]['bytes']}")
                
                fill_bytes = b'\x00' * (total_bytes - len(original_string))
                insert_string = original_string + fill_bytes

                # append the now binary value to the append string.
                append_string += insert_string
                index += 1
        # write every single data point in one go.
        try:
            with open(f"{self.directory}/{table_name}.bin", write_type+"b") as file:
                file.write(append_string)
        except:
            logging.error(f'{e}: unable to write data to file.')

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
    db.create_table("rentals", "apts", schema)
    # INSERT INTO apts (address, price, zip_code, bed, bath) VALUES ('123 Main St', 1500, '12345', 2, 1), ('456 Elm St', 2000, '23456', 3, 2), etc
    #d = db.execute({'operation': 'INSERT', 'columns': [], 'table': 'apts', 'values': data})
    #logging.info(d)
    # SELECT * FROM apts WHERE price < 1500
    data_list = db.execute({'operation': 'SELECT', 'columns': ['*'], 'table': 'apts', 'condition': {'column': 'price', 'operator': '<=', 'value': '2000'}})
    logging.info(f"data found: {data_list}")