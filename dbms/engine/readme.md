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

# Index Structure

Index sturctures are used to make conditional select queries faster. Table Objects are the primary users of index structres in our program. A typical execution of a SELECT WHERE statement would look like:

```
SELECT WHERE KEY... procedure:

1. Grab the query plan and identify that the plan contains a condition that uses the key of the index structure.
2. Search the index structure for file locations whose key matches the index structure and return a list of those file locations.
3. Grab only the data corresponding to the file locations provided by the index structure, resulting in a partial scan (which is faster than a full table scan)
```

### How to Index Scan?

**Engine** has the table object and info on the query plan. It should send the condition to the table.

**Table** has both the schema and the index structure. It should use the condition to figure out:
  1. Whether or not an index scan is faster (a.k.a see if the condition involves a key by using the schema.)
  2. If possible, tell the index structure to search itself for the key condition.

**Index Structure** is a data structure like a Hashmap, Bitmap, or Binary Tree. The data structure alot of functions, but the most important for index scans will be search (return a list of int's corresponding to the file location of selected rows.)

```
SELECT WHERE KEY pseudoscode:

# execute
DatabaseEngine.exeucte(query_plan):

  # If SELECT, run through general procedure
  DatabaseEngine.table_scan(condition):

    # Check speedup case
    Table.is_index_scannable(query_plan)

    # If a speedup case, get file locations 
    # for rows:
    locs = Table.index_structure.search(condition)

    # Read the data from the .bin file:
    data = DatabaseEngine.index_scan(query_plan["table"], locs)

    # return 
    return data
    
```