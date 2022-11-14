import json
from pymongo import MongoClient
from pymongo import TEXT

# Beginning of Phase 2. Don't know how to use pre-existing DBs so I made a new one again

client = MongoClient('mongodb://localhost:27016')

db = client["proj2"]

table = db["Table"]
db.table.create_index('year')

with open('dblp-ref-10.json') as file:
  for obj in file:
    file_data = json.loads(obj) 
    table.insert_one(file_data)

db.table.create_index( [("$**", TEXT)])
db.table.create_index("year")


results = table.find_one({"year":2009})
print(results)