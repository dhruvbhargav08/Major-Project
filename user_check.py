import pymongo

def check_data():
    try:
        mongo = pymongo.MongoClient(host="localhost", port=27017, serverSelectionTimeoutMS=1000)
        db = mongo.Major_Project
        mongo.server_info()
        data = db.Live_Test.find_one({"testid": 1})
        if data['laptop'] > 0 or data['cell_phone'] > 0 or data['book'] > 0 or data['tv'] > 0 or data['person'] > 1:
            return True
    except:
        print("ERROR")

# Call the function
result = check_data()
