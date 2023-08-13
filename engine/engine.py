import os

class DatabaseEngine:
    # stores all databases.
    def __init__(self, directory="os") -> None:
        self.directory = directory # for testing purposes. Either "os" (production) or "tmp_dir" (when testing)
        self.databases = [] # list of Database objects

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
        with open(db.name+"/"+table.name+".bin", "rb") as file:
            while True:
                rows = file.read(table.bytes_per_row)
                if not rows:
                    break
        return rows
    
    # create a table as a .bin file of the form table_name.bin
    def create_table(self, db: str, table_name: str):
        open(f"{self.directory}/{db}/{table_name}.bin", "wb")

    # create a database as a directory, where the directory/folder name is db_name
    def create_db(self, db_name: str):
        self.directory.mkdir(db_name)
        #db = Database(db_name)
        #self.databases.append(db)
    
    # completely delete the table from the database
    def drop_table(self, db_name: str, table_name: str):
        # search list of dbs
        for i in range(len(self.databases)):
            if self.databases[i].name == db_name:
                # search list of tables
                 for j in range(len(self.databases)):
                    if self.databases[i].tables[j] == table_name:
                        self.databases[i].tables.pop(j)
                        break
        os.remove(table_name+".bin")
        
    # completely delete the the database
    def drop_db(self, db_name: str):
        for i in range(len(self.databases)):
            if self.databases[i].name == db_name:
                self.databases.pop(i)
                break
        self.directory.rmdir(db_name)


    def print_db(self):
        print("Databases:")
        for db in self.databases:
            print(f"    {db.name}")
    
    def print_tables(self, db_name: str):
        db = ""
        for i in range(len(self.databases)):
            if self.databases[i].name == db_name:
                db = self.databases[i]
                break

        print(f"{db.name} Tables:")
        for table in db.tables:
            print(f"    {table}")
