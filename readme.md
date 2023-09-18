# Getting Started

Welcome to the DBMS project! This project features a subset of SQL and implements a database engine to process the SQL queries.

## Installation

Follow the installation steps below:

### 1. Clone the repo:
```
git clone https://github.com/nat-leo/dbms.git
```

### 2. Install the the package
You NEED to update pip to the latest version, and use the latest version of Python (3.11 as of 9/18/23)
Or you'll get build errors when running pip install. First, [update Python](https://www.python.org/downloads/), second:

```
pip install --upgrade pip
```
```
pip3 install --upgrade pip3
```

In order to get access to the REPL:
```
cd dbms
pip install .
```
OR if you're using python3 and pip3:
```
cd dbms
pip3 install .
```

And that should do it! Run either command below to start the REPL:

```
db -l
```
OR
```
db --login
```



## Basic Usage

#### WARNING: SQL reserved keywords like SELECT, UPDATE, etc must be ALL CAPS.
```
db --login
```
eate or login to a user with the name `test` and password `password`, then enter details when prompted:
```
% db --login
user: test
password: password
WARNING: t_ignore contains a literal backslash '\'
enter Q to exit
sql > 
```

Create a table easily with SQL:
```
sql > CREATE TABLE table (col varchar(255))
None
```
Add some data to your newly created table:
```
sql > INSERT INTO table (col) VALUES (bob)
None
sql >  INSERT INTO table (col) VALUES (bill)   
None
sql >  INSERT INTO table (col) VALUES (babs)
None
```

Currently you can only enter one row at a time, and will add an empty row:
```
sql > INSERT INTO table (col) VALUES (bob, bill, babs)
An Exception Occurred: list index out of range
None
```

Read the data you just wrote, including the empty row:
```
sql > SELECT * FROM table
[{'col': 'bob'}, {'col': 'bill'}, {'col': 'babs'}, {'col': ''}]
```
To quit:
```
sql > q
```

## Where Everything Is

There are a few quirks before we begin. First is that your data is stored in the engine dirctory (as opposed to var/lib or wherever):

```
dbms/ # the repo
├── ...
├── ...
├── ...
├── engine/ # the Database Engine
    ├── ...
    ├── ...
    ├── ...
    ├── database/ # user prompt in the REPL
        ├── hash.txt
        ├── salt.bin
        ├── table/
            ├── schema.json 
            └── table.bin # the actual data

```

**database/** is what you enter into the `user:` prompt when you initially start up the repo with:

```
db --login
```
**table/** is the directory that holds the relation's metadata and data. When you run `CREATE TABLE table`, you get this directory and the following:

**schema.json** holds the schema of your table, including the datatype and size in bytes of your columns.

**table.bin** has the actual data. SQL queries read, write, and modify this file.
