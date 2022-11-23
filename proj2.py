import json
from pymongo import MongoClient
from pymongo import TEXT
import pymongo

# Beginning of Phase 2. Don't know how to use pre-existing DBs so I made a new one again

client = MongoClient('mongodb://localhost:27016')

# client.drop_database("proj4")

db = client["proj4"]

table = db["Table"]

# with open('dblp-ref-1m.json') as file:
#    for obj in file:
#      file_data = json.loads(obj) 
#      table.insert_one(file_data)

# found = table.find_one({"id":"005ce28f-ed77-4e97-afdc-a296137186a1"})
# print(found)

# table.create_index( [("$**", 'text')])
# table.create_index("year")
# table.create_index([("references", pymongo.DESCENDING)])
# By changing the value of default_language in your create index command, you control whether stop words should or should not be indexed.

numArticles = 10
print("DONE")

part3 = table.aggregate(
    [
        { "$match" : {
          "venue": {"$ne":""}
        }},
      
        { "$lookup": {
          "from": "Table",
          "localField": "id",
          "foreignField": "references",
          "as": "articlesReferenced"
        }},

        { "$unwind": "$articlesReferenced" },
         
        { "$project": {
          "venue":1, "articlesReferenced.id":1
        }},

        { "$group" : {
          "_id" : "$venue",
          "ids_referencing_venue": {"$addToSet": "$articlesReferenced.id"},
        }},
         
        { "$project": {
          "venue":1, "referenceCount": {"$size": "$ids_referencing_venue"}
        }},

        { "$sort" : {
          "referenceCount":-1,
        }},

        { "$limit" : numArticles }
    ])
article_num = 1

venueCount = table.aggregate(
    [
      { "$group" : {
          "_id" : "$venue",
          "Number of Articles in Venue" : {"$sum" : 1}
        }},
        { "$sort" : {
          "Number of Articles in Venue":1,
        }}
    ])

listvenue = list(venueCount)
listPart3 = list(part3)

print("Top Venues:")
for i in range(0, len(listPart3)):

  print("\n---" + str(article_num) + "---")
  print("Venue: " + listPart3[i]['_id'])
  for j in range(0, len(listvenue)):
    if listvenue[j]['_id'] == listPart3[i]['_id']:
      print("Number of Articles in Venue: " + str(listvenue[j]['Number of Articles in Venue']))
  print("Number of Articles Referenced: " + str(listPart3[i]['referenceCount']))
  print()
  article_num = article_num + 1

# DONT WORK

# part3 = table.aggregate(
#     [
      
#         { "$lookup": {
#            "from": "Table",
#            "localField": "id",
#            "foreignField": "references",
#            "as": "articlesReferenced"
#          }},
#          {
#             "$project":
#             {
#                 "referenceCount": {"$size": "$articlesReferenced"}
#             }
#         },
#          {"$group" : 
#         {"_id" : "$venue",  
#          "Number of Articles in Venue" : {"$sum" : 1}, 
#         }},
#         {"$project":{
#             "venue":1, "Number of Articles in Venue": 1}
#           },
#       {"$sort" :{"Number of Articles in Venue":-1,}},
#       { "$limit" : numArticles }
#     ])

# for i in part3:
#   print(i)

# part3 = table.aggregate(
#     [{
#     "$group" : 
#         {"_id" : "$venue",  
#          "Number of Articles in Venue" : {"$sum" : 1}
#         }},
#         { "$project": {
#            "venue": 1, "Number of Articles in Venue": 1
#          }},
#         { "$lookup": {
#            "from": "Table",
#            "localField": "id",
#            "foreignField": "references",
#            "as": "number of references"
#          }},
    
#       {"$sort" :{"Number of Articles in Venue":-1,}},
#       { "$limit" : numArticles }
#     ])

# for i in part3:
#   print(i)

# part3 = table.aggregate(
#     [
#         { "$project": {
#             "number of references": 1
#          }},
#         { "$lookup": {
#           "from": "Table",
#           "localField": "id",
#           "foreignField": "references",
#           "as": "number of references"
#         }},
#       { "$limit" : numArticles }
#     ])

# for i in part3:
#     print(i)


# part3 = table.aggregate(
#     [{
#     "$group" : 
#         {"_id" : "$venue",  
#          "Number of Articles in Venue" : {"$sum" : 1}
#         }},
        
#         { "$lookup": {
#           "from": "Table",
#           "localField": "id",
#           "foreignField": "reference",
#           "as": "number of references"
#         }},
    
#       {"$sort" :{"number of references":-1,}},
#       { "$limit" : numArticles }
#     ])

# for i in part3:
#    print(i)

# part 4
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

validYearFound = False
while validYearFound == False:
  year = input("Enter a year: ")

  try:
    year = int(year)
    validYearFound = True
  except:
    print("Please enter a valid year.")


table.insert_one({"id":id, "title": title, "authors": authorsList, "year": year, "abstract": "", "venue": "", "references": [], "n_citations": 0})

found = table.find_one({"title":title})
print(found)

