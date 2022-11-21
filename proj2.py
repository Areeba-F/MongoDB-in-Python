import json
from pymongo import MongoClient
from pymongo import TEXT

# Beginning of Phase 2. Don't know how to use pre-existing DBs so I made a new one again

client = MongoClient('mongodb://localhost:27017')

db = client["proj2"]

# Create a collection called "Table", remove anything already inside and all existing indexes, if any 
articles_coll = db["articles_coll"]
articles_coll.delete_many({})
db.articles_coll.drop_indexes()

with open('dblp-ref-10.json') as file:
  for obj in file:
    file_data = json.loads(obj) 
    articles_coll.insert_one(file_data)

# Inserts a new field: the $year field converted to string
articles_coll.update_many(
  { },
  [
    {"$set": {"str_year": { "$toString": "$year" }}}
  ]
)
#articles_coll.create_index([("$**", TEXT)], default_language = "none") # Now text index will also apply to the str_year field
articles_coll.create_index([("title", TEXT), ("authors", TEXT), ("abstract", TEXT), ("venue", TEXT), ("year", TEXT)], default_language = "none")
articles_coll.create_index("id")
print(list(db.articles_coll.index_information()))

### 1 - functionality: search for articles
def search_article(keywords):
  # matches are in any of title, authors, abstract, venue and year fields
  # All keywords must be found in a match, thus each keyword is quoted
  keyword_str = ""
  for word in keywords:
    keyword_str += "\"{}\" ".format(word)

  print(keyword_str)
  
  results = db.articles_coll.find({"$text": {"$search": "{}".format(keyword_str)}})
  return results

def article_display_more_info(article):
  print("\n")
  for key in article.keys():
    if(key == "references"):
      # Query
      refs = list(articles_coll.find({"id": {"$in" : article[key]}})) #is this using the index correctly?
      # Output references
      ref_num = 1
      for i in range(0, len(refs)):
        print("\t---Reference #" + str(ref_num) + "---")
        print("\tid: " + refs[i]["id"])
        print("\ttitle: " + refs[i]["title"])
        print("\tyear: " + str(refs[i]["year"]) + "\n")
        ref_num += 1
    else:
      print(str(key) + ": " + str(article[key]))

def search_article_menu():
  keywords = input("Search for articles based on keyword(s): ").split()
  matches = list(search_article(keywords))
  #matches = search_article(keywords)
  #matches1 = search_article(keywords) #a separate cursor works, but seems hacky and may not be reliable...
  #print(type(matches[0]))
  #print(matches[0])
  result_num = 1

  # Search summary
  for i in range(0, len(matches)):
    print("\n---" + str(result_num) + "---")
    print("id: " + matches[i]["id"])
    print("title: " + matches[i]["title"])
    print("year: " + str(matches[i]["year"]))
    print("venue: " + matches[i]["venue"])
    result_num += 1
  
  """
  for art in matches:
    print("\n---" + str(result_num) + "---")
    print("id: " + art["id"])
    print("title: " + art["title"])
    print("year: " + str(art["year"]))
    print("venue: " + art["venue"])
    result_num += 1
  """

  # More info
  article_selection = int(input("Enter an article's number for more info, or \"0\" to return: "))
  if(article_selection == 0):
    return
  #print(matches.next())
  #for art in matches: 1
  #matches1.skip(article_selection-1) #doesn't work on a cursor that has already iterated
  #print(matches1.next())
  article_display_more_info(matches[int(article_selection) - 1])

### 2 - functionality: search for authors
def search_authors(keyword):
  """
  pipeline = [
    {
      "$group":
        {
          "_id": "authors",
          "count_": {}
        }
    }
  ]
  """
  results = db.articles_coll.find({"$text": {"$search": "{}".format(keyword)}})
  total_publications = 0
  print("search for author...")

def search_authors_menu():
  keyword = input("Enter one keyword to search for authors: ")
  results = search_authors(keyword)

def main():
  print("---Main Menu---\n1. Search for Articles")
  main_menu_selection = input("Select an Option: ")
  if(main_menu_selection == "1"):
    search_article_menu()

if __name__ == "__main__":
  main()