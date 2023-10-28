from pymongo.mongo_client import MongoClient

uri = "mongodb+srv://<username>:<password>@cluster0.wgrmih5.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
    
db = client.get_database('user_chat')
records = db.collect_user_data
new = {
    'name': 'ram',
    'roll_no': 321,
    'branch': 'it'
}
records.insert_one(new)