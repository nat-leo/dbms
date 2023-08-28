engine > engine.py
# The Database Engine

The database engine is responsible for:
1. Run File I/O and getting data out of disk and on to memory.
2. Control read/write/execute permissions for users.
3. Implement the index structure to speed up File I/O.
4. Execute query plans. (A.K.A Do all these things.)

A FileManager can do 1 and 2. The IndexStructure can do 3, and the DatabaseEngine can do 4 by composing the other two.

The only command any user of the DatabaseEngine should be: 

```
execute(arg: a query plan):
  return the data that fulfills the query plan
```

Everything else is under the hood.

## Under The Hood:

When `execute()` is run:
```
1. DatabaseEngine gets the query plan

2. DatabaseEngine sends command to IndexStructure. IndexStructure returns a list of file locations.

3. DatabaseEngine sends the command and list of file locations to FileManager. FileManager does the IO and returns data.
```

### The DatabaseEngine Object:
```
```

### The FileManager object:
```
```

### The Index Structure Object:
```
```

Usage:

Say we have a schema for a table and some data to put in it:
```
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
```

Create a table like this, where `rentals` is the name of the db, and `apts` is the name of the table:

```
db = DatabaseEngine("rentals")
db.create_table("rentals", "apts", schema)
```

With the table created, `SELECT * FROM apts` should give an empty string:
```
db.execute({'operation': 'SELECT', 'columns': ['*'], 'table': 'apts', 'condition': None})
```

Insert data like this:
```
db.execute({'operation': 'INSERT', 'columns': [], 'table': 'apts', 'values': data})
```
The following read:
```
db.execute({'operation': 'SELECT', 'columns': ['*'], 'table': 'apts', 'condition': None})
```
```
[{'address': '123 Main St', 'price': '1500', 'zip_code': '12345', 'beds': '2', 'baths': '1'}, {'address': '456 Elm St', 'price': '2000', 'zip_code': '23456', 'beds': '3', 'baths': '2'}, {'address': '789 Oak Ave', 'price': '1800', 'zip_code': '34567', 'beds': '1', 'baths': '1'}, {'address': '101 Pine Rd', 'price': '2200', 'zip_code': '45678', 'beds': '3', 'baths': '2'}, {'address': '222 Maple Dr', 'price': '2800', 'zip_code': '56789', 'beds': '4', 'baths': '3'}]
```

You can delete or modify data as well:
```
# Update
db.execute({'operation': 'UPDATE', 'columns': ['*'], 'table': 'apts', 'set': [{'column': 'price', 'value': '1500'}], 'condition': None})
db.execute({'operation': 'SELECT', 'columns': ['*'], 'table': 'apts', 'condition': None})
```
```
[{'address': '123 Main St', 'price': '1500', 'zip_code': '12345', 'beds': '2', 'baths': '1'}, {'address': '456 Elm St', 'price': '1500', 'zip_code': '23456', 'beds': '3', 'baths': '2'}, {'address': '789 Oak Ave', 'price': '1500', 'zip_code': '34567', 'beds': '1', 'baths': '1'}, {'address': '101 Pine Rd', 'price': '1500', 'zip_code': '45678', 'beds': '3', 'baths': '2'}, {'address': '222 Maple Dr', 'price': '1500', 'zip_code': '56789', 'beds': '4', 'baths': '3'}]
```
```
# Delete
db.execute({'operation': 'DELETE', 'columns': ['*'], 'table': 'apts', 'condition': None})
db.execute({'operation': 'SELECT', 'columns': ['*'], 'table': 'apts', 'condition': None})
```
```
[]
```
