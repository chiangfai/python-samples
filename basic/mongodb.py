import pymongo

client = pymongo.MongoClient(host="127.0.0.1", port=27018)
db = client.get_database("helloworld")
users_collection = db.get_collection("users")
users = users_collection.find()

for item in users:
    print(item['name'])


bean = users_collection.find_one({
    'name': 'zhangsan'
})
print(bean)