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
print(list(db.articles_coll.index_information()))

def search_article(keywords):
  # matches are in any of title, authors, abstract, venue and year fields
  # All keywords must be found in a match, thus each keyword is quoted
  keyword_str = ""
  for word in keywords:
    keyword_str += "\"{}\" ".format(word)

  print(keyword_str)
  
  #FIX me, have to somehow exclude the references field from the search pool
  results = db.articles_coll.find({"$text": {"$search": "{}".format(keyword_str)}})
  return results

def main():

  ### 1 - functionality: search for articles 
  keywords = input("Search for articles based on keyword(s): ").split()
  matches = search_article(keywords)
  result_num = 1
  for art in matches:
    print("---" + str(result_num) + "---")
    print("\tID: " + art["id"])
    print("\tTITLE: " + art["title"])
    print("\tYEAR: " + str(art["year"]))
    print("\tVENUE: " + art["venue"] + "\n")
    result_num += 1

if __name__ == "__main__":
  main()