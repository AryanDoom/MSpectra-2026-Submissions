import os

class GarbageCollector:
    """
    Handles safe deletion by moving flagged files to a temporary trash location.
    """
    def __init__(self, trash_dir="./trash"):
        self.trash_dir = trash_dir
        if not os.path.exists(self.trash_dir):
            os.makedirs(self.trash_dir)

    def collect(self, files_to_remove):
        """
        Takes a list of file metadata records, moves them to the trash,
        and returns metrics about reclaimed space.
        """
        print(f"Running Garbage Collection on {len(files_to_remove)} items...")
        reclaimed_bytes = 0
        deleted_count = 0
        removal_details = [] # List of (original_path, trash_path)

        for file_meta in files_to_remove:
            path = file_meta.get("path")
            if path and os.path.exists(path):
                try:
                    filename = os.path.basename(path)
                    # Add a tiny timestamp so it doesn't collide in the trash folder repeatedly
                    import time
                    new_path = os.path.join(self.trash_dir, f"{int(time.time())}_{filename}")
                    # Move to trash using os.replace to prevent Windows FileExistsError crashes
                    os.replace(path, new_path)
                    
                    reclaimed_bytes += file_meta.get("size", 0)
                    deleted_count += 1
                    removal_details.append((path, new_path))
                except Exception as e:
                    print(f"Could not garbage collect file {path}: {e}")
                    
        return deleted_count, reclaimed_bytes, removal_details

    def restore(self, file_meta):
        """
        Moves a file from its timestamped trash location back to its original home.
        """
        trash_path = file_meta.get("trash_path")
        original_path = file_meta.get("path")
        
        if not trash_path or not os.path.exists(trash_path):
            print(f"Error: Trash source {trash_path} not found.")
            return False
            
        try:
            # Ensure the original directory still exists
            os.makedirs(os.path.dirname(original_path), exist_ok=True)
            # Move back
            os.replace(trash_path, original_path)
            print(f"Restored: {original_path}")
            return True
        except Exception as e:
            print(f"Failed to restore {original_path}: {e}")
            return False
