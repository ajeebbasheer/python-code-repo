import csv
import sys,os
import json
import pymongo
import functools

def getCsvFromDb(dbname):
        conn_string = "mongodb://free_radius_user:free-radius@172.28.12.170/" + dbname
        client = pymongo.MongoClient(conn_string)
        db = client[dbname]
        collections = [_ for _ in db.collection_names()]
        for collection in collections:
                keys = {}
                col = db[collection]
                data = col.find()
                for doc in data:
                        for k, v in doc.items():
                                if (k != '_id'):
                                        if (not keys.get(k)):
                                                keys[k] = 1
                                        else:
                                                keys[k] +=1
                keylist = ','.join(keys.keys())
                filename = collection + '.csv'
                if keylist == "":
                        print(f"no document in {collection}")
                else:
                        export_cmd = "mongoexport --uri='mongodb://free_radius_user:free-radius@172.28.12.170/%s' --collection=%s --out=%s --type=csv --fields %s" %(
                                dbname,collection,filename,keylist)
                        os.system(export_cmd)
if __name__=="__main__":
        dbname = sys.argv[1]
        getCsvFromDb(dbname)
~
