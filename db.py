import pymongo

client = pymongo.MongoClient("localhost", 27017)
db = client.UserDB
userCollection = db.users

# data = [{"name": "Ahmed Raza", "email": "Ahmed123"}]

# userCollection.insert_many(data)

query = {"email":"Ahmed123"}


print((userCollection.find_one(query,{"_id":1})["_id"]))
# for x in userCollection.find_one(query):
#   print(x)