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

# Our Design Decisions 

# The Table Initialization Problem

Does a table populate itself?

```
class Table
    def fill_index_structure(self):
        ...
        ...
        ...
```
In this case, it'd be nice for Tables to own the ability to fill their index structure. Given that the index structure is a class itself and should be ruled over by the Table class, this makes sense. The idea is nice in theory, but the devil is in the details:

```
def fill_index_structure:
    for every row in the file: # problem line 
        insert the key-(file loc) pair into the ndex structure.
```

## Why It's Bad

### Single Responsibility Principle

1. A class should only do one thing.
2. No two classes should do the same thing.

The first problem is that our Table class is now reading a file, which breaks the Single Responsibility Principle (SRP). Both DatabaseEngine AND Table can scan a file for data.

### Don't Repeat Yourself

The second problem is that the Table read is nearly the exact same as the DatabaseEngine Table read, so now we're breaking Don't Repeat Yourself (DRY) as well.

```
  Engine        ->       Engine
  /    \        ->       /   \
 /      \       ->      /     \
IO      Table   ->    IO  --  Table
```

## Solutions that don't work:

### Let the index structure initialize itself:

This would fulfill SRP in that now the Table isn't initializing the Index Structure. It initializes itself.

This still doesn't fulfill DRY: then Index Structure instead of Table is duplicating code in DatabaseEngine.

### Stop duplicate code - create a FileManager:

This would let both the Engine and Table call the same method. Which would help with DRY. Because FileManager now runs reads, it now has single responsibility: both the Engine and Table can call it.

This doesn't fully give us SRP: A class does one thing implies that no two classes do the same thing. Despite the fact that the table is running `init_index_structure()` and not Engine's `table_scan()`, Table and Engine are still both reading tables, breaking the SRP's implication.

## What we're going with

Engine reads tables and sends the key-(file locs) pairs to Table. It fulfills both DRY and SRP:


### Don't Repeat Yourself:

Only Engine reads files, Table no longer needs to read a file in order to initialize its index.

### Single Responsibility Principle

Only Engine can read files. Only Table can initialize index structures.

When Engine initializes tables, reads the file for each table, and sends schema and data to the tables, which then saves the schema and initializes it's index structure by passing along the data to the index structure. The index structure then saves the data by building itself, and we're done!