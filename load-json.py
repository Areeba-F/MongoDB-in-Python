import json
import timeit
import os
import pymongo
from pymongo import MongoClient
from pymongo import TEXT

"""
with open('dblp-ref-10.json') as file:
  for obj in file:
    file_data = json.loads(obj) 
    articles_coll.insert_one(file_data)
"""

def main():
  # Input parameters
  #input_file = input("Enter input file name/path: ")
  port_num = input("Enter the port number the MongoDB server is running: ")
  
  # Initialize DB
  client = MongoClient("mongodb://localhost:{}".format(port_num))
  db = client["291db"]

  #collist = db.list_collection_names()
  #if "dblp" in collist:
    #db.dblp.drop() #or maybe articles_coll.delete_many({})
  dblp = db["dblp"]
  db.dblp.drop_indexes() #-- should not be necessary anymore, unless testing

  #json mongoimport
  #command = r'"D:\Program Files\MongoDB\Tools\100\bin\mongoimport.exe" --port={} --db=291db --collection=dblp --file={}'.format(port_num, input_file)
  #os.system(command)
  
  # Inserts a new field: the $year field converted to string
  new_column_st = timeit.default_timer()
  dblp.update_many(
  { },
  [
    {"$set": {"str_year1": { "$toString": "$year" }}}
  ]
  )
  new_column_elapsed = timeit.default_timer() - new_column_st

  #dblp.create_index([("$**", TEXT)], default_language = "none") # Now text index will also apply to the str_year field
  text_index_st = timeit.default_timer()
  dblp.create_index([("title", TEXT), ("authors", TEXT), ("abstract", TEXT), ("venue", TEXT), ("str_year", TEXT)], default_language = "none")
  text_index_elapsed = timeit.default_timer() - text_index_st
  
  id_index_st = timeit.default_timer()
  dblp.create_index("id")
  id_index_elapsed = timeit.default_timer() - id_index_st

  dblp.create_index([("references", pymongo.DESCENDING)])
  
  #debug
  print(list(db.dblp.index_information()))
  print("new_column_elapsed: ")
  print(new_column_elapsed)
  print("text_index_elapsed: ")
  print(text_index_elapsed)
  print("id_index_elapsed: ")
  print(id_index_elapsed)

if __name__ == "__main__":
  main()