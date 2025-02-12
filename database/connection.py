from pymongo import MongoClient

def get_mongo_client():
    """
    Returns a MongoDB client connected to the 'instagram' database.
    """
    MONGO_URI = "mongodb://172.31.208.235:27017"  # Update this if needed
    client = MongoClient(MONGO_URI)
    return client["instagram"]
