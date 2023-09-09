import argparse

from dbms.engine import engine
from dbms.compiler import parse

# dbms -r "SELECT * FROM relation"
def run_sql_query():
    # get args
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--run', action="store", help='run the following sql query.')
    parser.add_argument('-ls', '--list', action="store_true", help='list all tables for the given user')
    args = parser.parse_args()

    # set up database objects
    eng = engine.DatabaseEngine("root", "bill")
    sql = parse.Parser()
    if(args.list):
        tables = eng.ls()
        print(f"{eng.user} has the following tables:")
        for table in tables:
            print(f"* {table}")
    if(args.run):
        try:
            sql.parse(args.run)
            print(f"Query Plan:\n {sql.query_plan}")
        except:
            print(f"an exception occurred while parsing {args.run}")
        try:
            eng.execute(sql.query_plan)
        except:
            print(f"an exception occurred while executing {args.run}. Query plan:\n {sql.query_plan}")

