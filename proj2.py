import json
from pymongo import MongoClient
from pymongo import TEXT

# Phase one stuff
'''
client = MongoClient('mongodb://localhost:27016')
db = client["291db"]
# Create a collection called "Table", remove anything already inside and all existing indexes, if any 
dblp = db["dblp"]
dblp.delete_many({})
db.dblp.drop_indexes()
with open('dblp-ref-1m.json') as file:
  for obj in file:
    file_data = json.loads(obj) 
    dblp.insert_one(file_data)
# Inserts a new field: the $year field converted to string
dblp.update_many(
  { },
  [
    {"$set": {"str_year": { "$toString": "$year" }}}
  ]
)

#dblp.create_index([("$**", TEXT)], default_language = "none") # Now text index will also apply to the str_year field
dblp.create_index([("title", TEXT), ("authors", TEXT), ("abstract", TEXT), ("venue", TEXT), ("str_year", TEXT)], default_language = "none")
dblp.create_index("id")
print(list(db.dblp.index_information()))
'''
# Beginning of Phase 2
port_num = input("Enter the port number the MongoDB server is running: ")
client = MongoClient("mongodb://localhost:{}".format(port_num))
db = client["291db"]
collist = db.list_collection_names()
if "dblp" in collist:
  dblp = db["dblp"]

### 1 - functionality: search for articles
def search_article(keywords):
  # matches are in any of title, authors, abstract, venue and year fields
  # All keywords must be found in a match, thus each keyword is quoted
  keyword_str = ""
  for word in keywords:
    keyword_str += "\"{}\" ".format(word)

  print(keyword_str)
  
  results = db.dblp.find({"$text": {"$search": "{}".format(keyword_str)}})
  return results

def article_display_more_info(article):
  print("")
  for key in article.keys():
    if(key == "references"):
      # Query
      refs = list(dblp.find({"id": {"$in" : article[key]}})) #is this using the index correctly?
      # Output references
      for i in range(0, len(refs)):
        print("\t---Reference #" + str(i + 1) + "---")
        print("\tid: " + refs[i]["id"])
        print("\ttitle: " + refs[i]["title"])
        print("\tyear: " + str(refs[i]["year"]) + "\n")
    else:
      print(str(key) + ": " + str(article[key]))
  print("")

def search_article_menu():
  keywords = input("Search for articles based on keyword(s): ").split()
  matches = list(search_article(keywords))

  # Search summary FIX ME, IMPLEMENT PRINT SUMMARY FUNCTION
  for i in range(0, len(matches)):
    print("\n---" + str(i + 1) + "---")
    print("id: " + matches[i]["id"])
    print("title: " + matches[i]["title"])
    print("year: " + str(matches[i]["year"]))
    print("venue: " + matches[i]["venue"])

  # More info
  article_selection = int(input("Enter an article's number for more info, or \"0\" to return: "))
  if(article_selection == 0):
    return
  article_display_more_info(matches[article_selection - 1])

### 2 - functionality: search for authors
def search_authors(keyword):
  #FIX ME, compare execution time for using $text index $and regex search in authors field vs. just regex searching in authors
  pipeline = [
    {
      "$match":
        {
          "$and":[
            {"$text": {"$search": "{}".format(keyword)}},
            {"authors": {"$regex" : "{}".format(keyword), "$options" : "i"}}
          ]
        }
    },
    {
      "$unwind": "$authors"
    },
    {
      "$match":
        {
          "authors": {"$regex" : "{}".format(keyword), "$options" : "i"}
        }
    },
    {
      "$group":
        {
          "_id": "$authors",
          "count_publications": {"$sum": 1}
        }
    }
  ]
  
  author_results = db.dblp.aggregate(pipeline)
  return author_results

def author_display_publications(author):
  pipeline = [
    {
      "$match":
        {
          "$and":[
            {"$text": {"$search": "{}".format(author["_id"])}},
            {"authors": {"$regex" : "{}".format(author["_id"]), "$options" : "i"}}
          ]
        }
    },
    {
      "$sort": {"year": -1}
    },
    {
      "$project": {"_id": 0, "title": 1, "year": 1, "venue": 1}
    }
  ]
  author_publications = db.dblp.aggregate(pipeline)

  #display output, FIX me, implement separate functions
  for article in author_publications:
    print("")
    print("title: " + article["title"])
    print("year: " + str(article["year"]))
    print("venue: " + article["venue"])
  print("")

def search_authors_menu():
  keyword = input("Enter one keyword to search for authors: ")
  author_matches = list(search_authors(keyword))
  #FIX ME, IMPLEMENT PRINT SUMMARY FUNCTION
  #Search results summary
  for i in range(0, len(author_matches)):
    print("\n---" + str(i + 1) + "---")
    print("author name: " + author_matches[i]["_id"])
    print("number of publications: " + str(author_matches[i]["count_publications"]))
  
  author_selection = int(input("Enter an author's number to see their publications, or \"0\" to return: "))
  if(author_selection == 0):
    return
  author_display_publications(author_matches[author_selection - 1])

def top_venues():

    numArticles = input("How many top venues do you want to display? ")
    numArticles = int(numArticles)

    part3 = dblp.aggregate(
    [
        { "$match" : {
          "venue": {"$ne":""}
        }},
      
        { "$lookup": {
          "from": "dblp",
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

    venueCount = dblp.aggregate(
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

def insert_article():
    uniqueIdFound = False
    while uniqueIdFound == False:
        id = input("Enter a unique id: ")

        found_ids = dblp.find_one({"id":"id"})

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


    dblp.insert_one({"id":id, "title": title, "authors": authorsList, "year": year, "abstract": "", "venue": "", "references": [], "n_citations": 0})

    found = dblp.find_one({"title":title})
    print(found)


def main():
  while(True):
    print("---Main Menu---\n1. Search for Articles \n2. Search for Authors \n3. Get the top venues \n4. Insert new article")
    main_menu_selection = input("Select an Option: ")
    if(main_menu_selection == "1"):
      search_article_menu()
    if(main_menu_selection == "2"):
      #under development...
      search_authors_menu()
    if(main_menu_selection == "3"):
      top_venues()
    if(main_menu_selection == "4"):
      insert_article()
  
if __name__ == "__main__":
  main()