# DBMS

This project is an implementation of a DBMS like PostgreSQL or MySQL (but watered down) for the purpose of learning more about the implementation of said systems.

## The Architecture

file structure shown below:

```
sql-dbms
├── Engine
└── SQL Compiler
    └── Parser
```

### Database Engine

The system is composed of the Database Engine that runs physical query plans by accessing, editing, and reading directories and files.

### SQL Compiler

Parsing SQL queries is left to the compiler, which supports a subset of the SQL language. The compiler parses an sql query and sends that query to the Database Engine as a Logical Query Plan.

