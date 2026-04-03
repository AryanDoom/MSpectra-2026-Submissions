try:
    from pymongo import MongoClient
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False
    print("pymongo not installed, using memory mock database.")

class DatabaseManager:
    """
    Handles connections to MongoDB and operations related to file metadata.
    Includes a fallback in-memory mock if MongoDB is unavailable.
    """
    def __init__(self, db_uri="mongodb://localhost:27017/"):
        if MONGO_AVAILABLE:
            self.client = MongoClient(db_uri)
            self.db = self.client['storage_optimization']
            self.collection = self.db['files']
            self.mock_db = None
        else:
            self.client = None
            self.collection = None
            self.mock_db = {}

    def insert_or_update(self, metadata):
        """
        Inserts new metadata or updates it if the file path already exists.
        """
        file_path = metadata.get("path")
        if MONGO_AVAILABLE:
            self.collection.update_one(
                {"path": file_path}, 
                {"$set": metadata}, 
                upsert=True
            )
        else:
            # For the mock DB, we can just key by the file hash or path
            self.mock_db[file_path] = metadata

    def check_fast_hash(self, fast_hash, file_path):
        """Tier 1 Deduplication Check: Returns path of existing sibling if first megabyte matches."""
        if not fast_hash: return None
        if MONGO_AVAILABLE:
            existing = self.collection.find_one({"fast_hash": fast_hash})
            if existing and existing["path"] != file_path:
                return existing["path"]
            return None
        else:
            for path, meta in self.mock_db.items():
                if meta.get("fast_hash") == fast_hash and path != file_path:
                    return path
            return None

    def check_full_hash(self, full_hash, file_path):
        """Tier 2 Verification: Returns path if 100% cryptographic match exists."""
        if not full_hash: return None
        if MONGO_AVAILABLE:
            existing = self.collection.find_one({"full_hash": full_hash})
            if existing and existing["path"] != file_path:
                return existing["path"]
            return None
        else:
            for path, meta in self.mock_db.items():
                if meta.get("full_hash") == full_hash and path != file_path:
                    return path
            return None

    def get_removable_files(self):
        """
        Returns a list of file metadata dictionaries that are marked Redundant or are Duplicates.
        """
        if MONGO_AVAILABLE:
            candidates = self.collection.find(
                {"$or": [{"classification": "Redundant"}, {"is_duplicate": True}]}
            )
            return list(candidates)
        else:
            candidates = []
            for meta in self.mock_db.values():
                if meta.get("classification") == "Redundant" or meta.get("is_duplicate") == True:
                    candidates.append(meta)
            return candidates

    def mark_as_removed(self, file_path, trash_path):
        """
        Marks a file as optimized/trashed and stores the link to its location in /trash.
        """
        if MONGO_AVAILABLE:
            self.collection.update_one(
                {"path": file_path}, 
                {"$set": {"status": "trashed", "trash_path": trash_path}}
            )
        else:
            if file_path in self.mock_db:
                self.mock_db[file_path]["status"] = "trashed"
                self.mock_db[file_path]["trash_path"] = trash_path

    def get_removed_record(self, file_path):
        """
        Retrieves the metadata for a trashed file using its original path.
        """
        if MONGO_AVAILABLE:
            return self.collection.find_one({"path": file_path, "status": "trashed"})
        else:
            meta = self.mock_db.get(file_path)
            if meta and meta.get("status") == "trashed":
                return meta
            return None
