from pymongo import MongoClient
from typing import Dict

def get_mongo_client() -> MongoClient:
    """
    Returns a MongoDB client connected to the 'instagram' database.
    """
    client = MongoClient("mongodb://172.31.208.235:27017")  # Adjust if you have a different URI
    return client["instagram"]

def save_to_mongo(collection_name: str, data: Dict) -> None:
    """
    Saves data to the specified MongoDB collection.
    
    Parameters:
        collection_name (str): Name of the MongoDB collection.
        data (Dict): Data to be saved in the collection.
    """
    db = get_mongo_client()
    collection = db[collection_name]
    collection.insert_one(data)

save_to_mongo("likers", data = {"name": "Alireza", "lastname": "Farjami"})