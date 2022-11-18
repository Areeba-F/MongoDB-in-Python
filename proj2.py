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

db.articles_coll.create_index([("$**", TEXT)])
#db.articles_coll.create_index([('abstract', 'text')], name='article_abstract')
db.articles_coll.create_index("year")
print(list(db.articles_coll.index_information()))

def search_article(keywords_str):
  # matches are in any of title, authors, abstract, venue and year fields
  results = db.articles_coll.find({"$text": {"$search": "{}".format(keywords_str)}})
  return results

def main():
  
  keywords_str = "purpose develop"
  matches = search_article(keywords_str)
  
  # for each matching article, display the id, the title, the year and the venue fields.
  for art in matches:
    print("ID:" + art["id"] + "    TITLE:" + art["title"] + "    YEAR:" + str(art["year"]) + "    VENUE:" + art["venue"])


if __name__ == "__main__":
  main()
#results = articles_coll.find_one({"year":2009})
#print(results)