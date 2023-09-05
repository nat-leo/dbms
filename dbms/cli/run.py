import argparse

# dbms -r "hgello"
def my_func():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--run', action="store", help='run the following sql query.')
    args = parser.parse_args()
    print(f"yo. {args.run}")
