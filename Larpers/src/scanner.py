import os
import hashlib
from datetime import datetime

class FileScanner:
    """
    Handles directory traversal, metadata extraction, and content hashing.
    """
    def __init__(self, target_directory):
        self.target_directory = target_directory
        self.queue = []

    def scan_directory(self):
        """
        Recursively scans the target directory and populates the file queue.
        """
        print(f"Scanning directory: {self.target_directory}")
        for root, _, files in os.walk(self.target_directory):
            for file in files:
                file_path = os.path.join(root, file)
                self.queue.append(file_path)
        print(f"Discovered {len(self.queue)} files.")
        return self.queue

    def compute_file_hash(self, file_path):
        """
        Computes the SHA-256 hash of a file for content-based deduplication.
        Handles large files by reading in chunks.
        """
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                # Read file in 4MB chunks
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            print(f"Error computing hash for {file_path}: {e}")
            return None

    def compute_fast_hash(self, file_path):
        """
        Computes a quick fingerprint by hashing ONLY the first 1 Megabyte of data.
        """
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                chunk = f.read(1048576) # Exactly 1 MB
                sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except:
            return None

    def extract_metadata(self, file_path):
        """
        Extracts foundational metadata (size, access time, and deep semantic heuristics).
        """
        try:
            stat = os.stat(file_path)
            fast_hash = self.compute_fast_hash(file_path)
            
            # Simple File Extension Extraction
            _, ext = os.path.splitext(file_path)
            ext = ext.lower()
            if ext == "": ext = ".unknown"
            
            # Semantic & Structural Heuristics
            # 1. Path Depth: Deeper paths = higher chance of junk
            path_depth = len(file_path.split(os.sep))
            
            # 2. Key Directories: Identifying heavily bloated generic folders
            path_lower = file_path.lower()
            is_temp_dir = 1 if any(kw in path_lower for kw in ['temp', 'tmp', 'cache', 'build', '__pycache__', 'node_modules']) else 0
            
            # 3. Filename Semantics: Humans append massive keywords to useless duplications
            has_backup_keyword = 1 if any(kw in path_lower for kw in ['copy', 'backup', 'old', 'final', 'v2', 'v3', 'test']) else 0
            
            metadata = {
                "path": file_path,
                "size": stat.st_size,
                "last_access": stat.st_atime,
                "fast_hash": fast_hash,
                "full_hash": None, # Heavy Hash securely deferred 
                "extension": ext,
                "path_depth": path_depth,
                "is_temp_dir": is_temp_dir,
                "has_backup_keyword": has_backup_keyword,
                "is_similar_to": None, # Will be populated by the DB/Orchestrator
                "timestamp": datetime.now().isoformat()
            }
            return metadata
        except Exception as e:
            print(f"Failed to extract metadata for {file_path}: {e}")
            return None
