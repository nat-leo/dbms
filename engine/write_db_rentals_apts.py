from test.apt_data import schema, data
import engine as e

def test():
    db = e.DatabaseEngine()
    db.create_db("rentals")
    db.create_table("rentals", "apts", schema)
    db.insert("rentals", "apts", data)

if __name__ == "__main__":
    test()