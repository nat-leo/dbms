dbms > engine > bst.py

# Binary Search Trees
A common sight as index structures for DBMSes. Balanced ones provide:

1. **O(log(n)) Search time**
2. **O(log(n)) Insert time**
3. **O(log(n)) Delete time**
4. **O(k + log(n)) Range Query on Key** (when the range in question is the key used to build the bst.)
4. **O(n) Range Query off Key** (when the range in question is not the key used to build the bst. 
Or the range covers the entire tree.)

Where n is the number of elements, and log(n) is the height of the tree, k is th enumber of keys in the range.

## As index structures

### Keeping it log(n)

O(log(n)) scans only happen when SQL queries involve:
1. the key used to build the bst.
2. a small range

```
# price makes a good key for a bst if WHERE uses the price column the most:

SELECT * FROM rentals WHERE price < 5
SELECT address, price, beds, bath, zipcode WHERE price <= 1500
```

```
# building a bst using price as the key doesn't help the second SQL query:

SELECT * FROM rentals WHERE price < 5
SELECT address, price, beds, bath, zipcode WHERE beds = 1
```

Make sure to pick an attribute that gets queried the most as a condition. Since this attribute is the key used to build the bst, only conditional queries that use the key will be sped up by using a bst. Other queries will result in the engine having to scan the entire data structure, resulting in O(n) searches. 

If the attribute often shows up as a condition, but the condition range always encompasses almost all the data in the index structure, try the next most used attribute in conditions. Ranges that use the key attribute, but also access a sigificantly high propertion of the data may also result in O(n) searches.

```
# with price as the key and the range of the condition so wide, why bother:

SELECT address, price, beds, bath, zipcode WHERE 0 <= price = 1,000,000,000,000,000,000,000,000,000,000.00
```