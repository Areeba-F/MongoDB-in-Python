import json
from pymongo import MongoClient
from pymongo import TEXT

# Beginning of Phase 2. Don't know how to use pre-existing DBs so I made a new one again

client = MongoClient('mongodb://localhost:27016')

client.drop_database("proj3")

db = client["proj3"]

table = db["Table"]

with open('dblp-ref-1k.json') as file:
   for obj in file:
     file_data = json.loads(obj) 
     table.insert_one(file_data)

found = table.find_one({"id":"005ce28f-ed77-4e97-afdc-a296137186a1"})
print(found)

table.create_index( [("$**", 'text')])
table.create_index("year")
# By changing the value of default_language in your create index command, you control whether stop words should or should not be indexed.

numArticles = 10
print("DONE")


part3 = table.aggregate(
    [{
    "$group" : 
        {"_id" : "$venue",  
         "Number of Articles in Venue" : {"$sum" : 1}
        }},
        
        { "$lookup": {
          "from": "Table",
          "localField": "reference",
          "foreignField": "id",
          "as": "number of references"
        }},
    
      {"$sort" :{"number of references":-1,}},
      { "$limit" : numArticles }
    ])

for i in part3:
    print(i)

uniqueIdFound = False
while uniqueIdFound == False:
  id = input("Enter a unique id: ")

  found_ids = table.find_one({"id":"id"})

  if found_ids != None:
    print("That id is already taken.")

  else:
    uniqueIdFound = True

title = input("Enter a title: ")

authors = input("Enter a list of authors (seperated by commas)")
authorsList = authors.split(",")

isValid = False
while isValid == False:
  year = input("Enter a year: ")

  try:
    year = int(year)
    isValid = True
  except:
    print("Please enter a valid year.")


table.insert_one({"id":id, "title": title, "authors": authorsList, "year": year, "abstract": None, "venue": None, "references": [], "n_citations": 0})

found = table.find_one({"title":title})
print(found)

