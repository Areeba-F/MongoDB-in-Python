import json
from pymongo import MongoClient
from pymongo import TEXT

# TODO: actually make this a user input
client = MongoClient('mongodb://localhost:27016')

db = client["291db"]

table = db["dblp"]

# load file line by line
with open('dblp-ref-1m.json') as file:
  for obj in file:
    file_data = json.loads(obj)
    table.insert_one(file_data)

# index
db.table.create_index( [("$**", TEXT)])
db.table.create_index("year")

print("done")