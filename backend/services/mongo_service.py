import bson
import datetime
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent))

from backend.config.settings import get_settings
from logging_system import error, warning

class MongoService:
    def __init__(self):
        self.settings = get_settings()
        self.database = None
        self._initialize_mongo()
    
    def _initialize_mongo(self):
        """Initialize MongoDB connection"""
        try:
            connection_string = self.settings.mongo_connection_string
            mongo_client = MongoClient(connection_string)
            self.database = mongo_client.get_database("ellipsoid")
        except Exception as e:
            error(f"Error initializing MongoDB: {e}")
            raise
    
    def get_collection(self, collection_name: str):
        """Get a specific collection"""
        return self.database.get_collection(collection_name)
    
    # Generic CRUD operations for any collection
    def create_document(self, collection_name: str, document: dict) -> str:
        """Create a document in any collection"""
        try:
            collection = self.get_collection(collection_name)
            result = collection.insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            error(f"Error creating document in {collection_name}: {e}")
            raise
    
    def list_documents(self, collection_name: str, query: dict = None, sort: dict = None) -> list:
        """List documents from any collection"""
        try:
            collection = self.get_collection(collection_name)
            cursor = collection.find(query or {})
            if sort:
                cursor = cursor.sort(sort)
            return list(cursor)
        except Exception as e:
            error(f"Error listing documents from {collection_name}: {e}")
            return []
    
    def read_document(self, collection_name: str, document_id: str) -> dict:
        """Read a document from any collection"""
        try:
            collection = self.get_collection(collection_name)
            return collection.find_one({"_id": bson.ObjectId(document_id)})
        except Exception as e:
            error(f"Error reading document from {collection_name}: {e}")
            return None
    
    def update_document(self, collection_name: str, document_id: str, update_data: dict) -> bool:
        """Update a document in any collection"""
        try:
            collection = self.get_collection(collection_name)
            result = collection.update_one(
                {"_id": bson.ObjectId(document_id)}, 
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            error(f"Error updating document in {collection_name}: {e}")
            return False
    
    def delete_document(self, collection_name: str, document_id: str) -> bool:
        """Delete a document from any collection"""
        try:
            collection = self.get_collection(collection_name)
            result = collection.delete_one({"_id": bson.ObjectId(document_id)})
            return result.deleted_count > 0
        except Exception as e:
            error(f"Error deleting document from {collection_name}: {e}")
            return False
    
    def find_documents(self, collection_name: str, query: dict, sort: dict = None, limit: int = None) -> list:
        """Find documents matching specific criteria"""
        try:
            collection = self.get_collection(collection_name)
            cursor = collection.find(query)
            if sort:
                cursor = cursor.sort(sort)
            if limit:
                cursor = cursor.limit(limit)
            return list(cursor)
        except Exception as e:
            error(f"Error finding documents in {collection_name}: {e}")
            return []
    
    def count_documents(self, collection_name: str, query: dict = None) -> int:
        """Count documents in a collection"""
        try:
            collection = self.get_collection(collection_name)
            return collection.count_documents(query or {})
        except Exception as e:
            error(f"Error counting documents in {collection_name}: {e}")
            return 0
    

    
    def get_system_prompt(self, prompt_type: str = "system") -> str:
        """Retrieve system prompt from SubjectPrompts collection"""
        try:
            # Query for system prompt document - handle both quoted and unquoted field names
            prompt_doc = self.find_documents("SubjectPrompts", {"type": prompt_type}, limit=1)
            if not prompt_doc or len(prompt_doc) == 0:
                # Try with quoted field names (current MongoDB document structure)
                prompt_doc = self.find_documents("SubjectPrompts", {'"type"': prompt_type}, limit=1)
            
            if prompt_doc and len(prompt_doc) > 0:
                doc = prompt_doc[0]
                # Try both quoted and unquoted field names
                text = doc.get("text") or doc.get('"text"', "")
                return text
            else:
                warning(f"Warning: No system prompt found in SubjectPrompts collection for type '{prompt_type}'")
                return ""
        except Exception as e:
            error(f"Error retrieving system prompt from MongoDB: {e}")
            return ""

    # Settings-specific methods
    def get_user_settings(self, user_id: int) -> dict:
        """Get settings for a specific user"""
        try:
            settings_docs = self.find_documents("Settings", {"userId": user_id}, limit=1)
            if settings_docs and len(settings_docs) > 0:
                return settings_docs[0]
            return None
        except Exception as e:
            error(f"Error retrieving user settings for {user_id}: {e}")
            return None

    def upsert_user_settings(self, user_id: int, settings: dict) -> str:
        """Create or update user settings (upsert)"""
        try:
            collection = self.get_collection("Settings")
            
            # Check if settings already exist for this user
            existing_settings = collection.find_one({"userId": user_id})
            
            if existing_settings:
                # Update existing document - preserve the _id
                settings["_id"] = existing_settings["_id"]
                current_time = datetime.datetime.now(datetime.timezone.utc)
                settings["metadata"]["updatedAt"] = current_time
                # Keep the original createdAt timestamp
                if "createdAt" not in settings["metadata"]:
                    settings["metadata"]["createdAt"] = existing_settings["metadata"]["createdAt"]
                
                result = collection.replace_one(
                    {"_id": existing_settings["_id"]}, 
                    settings
                )
                if result.modified_count > 0:
                    return str(existing_settings["_id"])
                else:
                    raise Exception("Failed to update settings document")
            else:
                # Create new document
                current_time = datetime.datetime.now(datetime.timezone.utc)
                settings["metadata"]["createdAt"] = current_time
                settings["metadata"]["updatedAt"] = current_time
                result = collection.insert_one(settings)
                return str(result.inserted_id)
        except Exception as e:
            error(f"Error upserting user settings for {user_id}: {e}")
            raise

    def update_user_settings(self, user_id: int, update_data: dict) -> bool:
        """Update existing user settings"""
        try:
            collection = self.get_collection("Settings")
            
            # Add updatedAt timestamp
            update_data["metadata.updatedAt"] = datetime.datetime.now(datetime.timezone.utc)
            
            result = collection.update_one(
                {"userId": user_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            error(f"Error updating user settings for {user_id}: {e}")
            return False
