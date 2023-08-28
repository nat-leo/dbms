import os
import shutil
import engine as e

db = e.DatabaseEngine()

print(db.directory)

try:
    db.create_db("rentals")
    db.create_table("rentals", "apts", {"address": {"type": str,
                                                    "bytes": 64}, 
                                        "price": {"type": int,
                                                "bytes": 5}, 
                                        "zipcode": {"type": int,
                                                    "bytes": 5}})

    db.insert("rentals", "apts", [{"address": "1211 Make Believe Way, Park City, Utah",
                                "price": 1200,
                                "zipcode": 84060},{"address": "1211 Make Believe Way, Park City, Utah",
                                "price": 1200,
                                "zipcode": 84060}])
    
    print(db.scan("rentals", "apts", {'column': 'price', 'operator': '==', 'value': 1200}))

finally:
    #print("success!")
    shutil.rmtree(db.directory)
