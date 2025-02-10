from typing import Dict, Optional
from database.connection import get_mongo_client

db = get_mongo_client()

def save_to_mongo(collection_name: str, data: Dict) -> None:
    """
    Saves data to the specified MongoDB collection.
    
    Parameters:
        collection_name (str): Name of the MongoDB collection.
        data (Dict): Data to be saved in the collection.
    """
    try:
        collection = db[collection_name]
        collection.insert_one(data)
        print(f"✅ Data saved successfully in collection: {collection_name}")
    except Exception as e:
        print(f"❌ Error saving data to MongoDB: {e}")


def get_from_mongo(collection_name: str, query: Dict) -> Optional[Dict]:
    """
    Retrieves a document from the specified MongoDB collection.
    
    Parameters:
        collection_name (str): Name of the MongoDB collection.
        query (Dict): Query to fetch the document.
        
    Returns:
        Optional[Dict]: The document if found, else None.
    """
    try:
        collection = db[collection_name]
        result = collection.find_one(query)
        return result
    except Exception as e:
        print(f"❌ Error retrieving data from MongoDB: {e}")
        return None


def update_mongo(collection_name: str, query: Dict, update_data: Dict) -> None:
    """
    Updates a document in the specified MongoDB collection.
    
    Parameters:
        collection_name (str): Name of the MongoDB collection.
        query (Dict): Query to find the document.
        update_data (Dict): Data to update the document.
    """
    try:
        collection = db[collection_name]
        collection.update_one(query, {"$set": update_data}, upsert=True)
        print(f"✅ Data updated successfully in collection: {collection_name}")
    except Exception as e:
        print(f"❌ Error updating data in MongoDB: {e}")


def save_user_credentials(data: Dict) -> None:
    """
    Saves user credentials (including cookies) to MongoDB.

    Parameters:
        data (Dict): User credentials with cookies.
    """
    try:
        collection = db["user_credentials"]
        collection.update_one({"username": data["username"]}, {"$set": data}, upsert=True)
        print(f"✅ User credentials saved for {data['username']}")
    except Exception as e:
        print(f"❌ Error saving user credentials: {e}")

def get_user_credentials(username: str) -> Optional[Dict]:
    """
    Retrieves user credentials (including cookies) from MongoDB.

    Parameters:
        username (str): The username to search for.

    Returns:
        Optional[Dict]: User credentials if found, else None.
    """
    try:
        collection = db["user_credentials"]
        return collection.find_one({"username": username})
    except Exception as e:
        print(f"❌ Error retrieving user credentials: {e}")
        return None

def load_extracted_parameters(extract_username: str) -> dict:
    """
    Loads extracted parameters for a given Instagram username from MongoDB.
    
    Parameters:
    - extract_username: The username from which we will extract the session and other parameters.
    
    Returns:
    - A dictionary of extracted parameters.
    """
    user_data = get_user_credentials(extract_username)
    if user_data and "parameters" in user_data:
        return user_data["parameters"]
    
    print(f"❌ No extracted parameters found for user {extract_username}.")
    return {}