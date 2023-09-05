dbms > engine > hashmap.py

# Hashmaps
A common sight as index structures for DBMSes. As long as the Hashmap fits in memory:

1. **O(1) Search time**
2. **O(1) Insert time**
3. **O(1) Delete time**
4. **O(n) Range Query on Key** 
4. **O(n) Range Query off Key**

Where n is the number of rows in the table/relation, a possibly massive amount of data.

## As index structures

Hashmaps provide constant lookup on exact match queries:
```
SELECT * FROM apts WHERE price = 1500
```
But are O(n) on range queries because hashmaps are unsorted (you have to check the condition on each key):
```
SELECT * FROM apts WHERE price < 1500
```
They're much simpler to implement than your own Binary Search Tree, though. 

## Speeding up Range Queries

The unsorted bit can be solved by having an array of keys in sorted order to chnage O(n) to O(k+log(n)):

The pseudocode:
```
Ingredients:
 - One hashmap
 - One list of sorted keys

Recipe:
1. Binary search list of sorted keys for range bound: O(log(n)).
2. Once bound is found: move away from the bound until you reach end of list or second bound: O(k)
3. During part 2, collect the file locations of the keys by accessing the hashmap. 
```