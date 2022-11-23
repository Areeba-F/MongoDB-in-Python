import json
from pymongo import MongoClient
from pymongo import TEXT
import pymongo

# Beginning of Phase 2. Don't know how to use pre-existing DBs so I made a new one again

client = MongoClient('mongodb://localhost:27016')
client.drop_database("proj4")
db = client["proj4"]
table = db["Table"]


table.create_index([("references", pymongo.DESCENDING)])

numArticles = 10
print("DONE")

def search_venue():

  venues = table.aggregate(
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

  listVenueCount = list(venueCount)
  listvenue = list(venues)

  print_venues(listVenueCount,listvenue)


def print_venues(listVenueCount,listvenue):
  print("Top Venues:")
  article_num = 1
  for i in range(0, len(listvenue)):

    print("\n---" + str(article_num) + "---")
    print("Venue: " + listvenue[i]['_id'])
    for j in range(0, len(listVenueCount)):
      if listvenue[j]['_id'] == listvenue[i]['_id']:
        print("Number of Articles in Venue: " + str(listVenueCount[j]['Number of Articles in Venue']))
    print("Number of Articles Referenced: " + str(listvenue[i]['referenceCount']))
    print()
    article_num = article_num + 1

# part 4

def add_article():
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

