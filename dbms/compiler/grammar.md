# 1. SQL Statements

This is the spec including grammar and examples of SQL statements that our compiler should be able to accept.

## Select
#### Select all columns from table 
```
SELECT * FROM employees;
```
#### Select with condition
```
SELECT product_name, price FROM products
WHERE price > 20;
```
#### Select with multiple conditions
```
SELECT order_id, order_date FROM orders
WHERE order_status = 'shipped' AND total_amount > 100;
```

## Insert
#### Basic insert:
```
INSERT INTO employees (employee_id, first_name, last_name, salary)
VALUES (1, 'John', 'Doe', 50000);
```
#### Insert multiple values:
```
INSERT INTO products (product_id, product_name, price)
VALUES
    (101, 'Widget A', 10.99),
    (102, 'Widget B', 15.99),
    (103, 'Widget C', 12.49);
```
#### Insert with Subquery
```
INSERT INTO sales (product_id, sale_date, quantity)
SELECT product_id, '2023-08-16', 5
FROM products
WHERE product_name = 'Widget A';
```
#### Insert with default values
```
INSERT INTO customers (customer_name, email)
VALUES ('Jane Smith', DEFAULT);
```

## Delete
#### Delete all rows from table
```
DELETE FROM products
```
#### Delete based on condition
```
DELETE FROM products
WHERE stock_quantity < 10;
```
#### Delete with subquery
```
DELETE FROM suppliers
WHERE supplier_id IN (
    SELECT supplier_id
    FROM products
    WHERE price < 10
);
```

## Update
#### Update single column in all rows
```
UPDATE employees
SET salary = salary * 1.1;
```
#### Update single column in rows where the condition is true
```
UPDATE products
SET stock_quantity = stock_quantity - 1
WHERE product_id = 101;
```
#### Update mulitple columns in rows where the condition is true
```
UPDATE orders
SET order_status = 'shipped', shipping_date = '2023-08-16'
WHERE order_id = 1001;
```

# 2. The SQL Grammar
The grammar is as follows:

## Tokens

Below are the reserved keywords for SQL. Organized by type of SQL operation. 
```
# Select
SELECT
FROM
WHERE 
AND
# Insert
INSERT INTO
VALUES
# Delete
DELETE FROM
# Update
UPDATE
SET
```
Aside from those, we also need every single comparison operator: **<, <=, ==, =>, >, etc** as well as brackets and parenthesis **()[]**. Also commas and asterisks...

## Grammar

The production rules are below. Given the implementation will be a **Recursive Descent Parser**, the grammar will be carefully written. It must be:

1. Non-ambiguous
2. Non-left recursive
3. predictive

### SQL production rules
```
query ::= select
        | insert
        | update
        | delete

select ::= SELECT column_list FROM table options

column_list ::= column
              | ASTERISK
              | column_list COMMA column
column ::= ID
table ::= ID

options ::= WHERE condition
          | empty

condition ::= column operator value
operator ::= <|>|<=|>=|=|IN
value ::= NUM|LIST|STRING

insert ::= INSERT INTO table schema VALUES values_list

values_list ::= value
              | values_list COMMA value
value ::= ( attributes_list )

attributes_list ::= attribute
                  | attributes_list COMMA attribute
attribute ::= NUM|LIST|STRING
```