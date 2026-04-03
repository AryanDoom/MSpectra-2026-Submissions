import os
import bsdiff4
import hashlib

class DeltaManager:
    """
    Handles Binary Delta Compression between similar files.
    Allows for 'Ghost Files' to be stored as tiny patches.
    """
    def __init__(self, delta_storage_dir="deltas"):
        self.delta_storage_dir = delta_storage_dir
        if not os.path.exists(self.delta_storage_dir):
            os.makedirs(self.delta_storage_dir)

    def create_delta(self, base_file, similar_file):
        """
        Calculates the binary difference between base and similar, 
        saves a .patch file, and returns the path to the patch.
        """
        try:
            # Generate a unique patch filename based on the similar file's name
            patch_name = f"{os.path.basename(similar_file)}.patch"
            patch_path = os.path.join(self.delta_storage_dir, patch_name)
            
            # Binary Delta Calculation (bsdiff)
            bsdiff4.file_diff(base_file, similar_file, patch_path)
            
            # Calculate Savings
            original_size = os.path.getsize(similar_file)
            patch_size = os.path.getsize(patch_path)
            savings = original_size - patch_size
            
            print(f"Delta created: {patch_name} ({patch_size / 1024:.2f} KB). Saved {savings / (1024*1024):.2f} MB")
            return patch_path, savings
        except Exception as e:
            print(f"Error creating delta: {e}")
            return None, 0

    def reconstruct_file(self, base_file, patch_file, output_path):
        """
        Stitches the base file and the patch together to recreate the original file.
        """
        try:
            bsdiff4.file_patch(base_file, patch_file, output_path)
            return True
        except Exception as e:
            print(f"Error reconstructing file: {e}")
            return False

    def verify_reconstruction(self, base_file, patch_file, original_hash):
        """
        Dry-runs a reconstruction and verifies the SHA-256 hash matches 100%.
        """
        temp_path = "temp_reconstruction.bin"
        try:
            if self.reconstruct_file(base_file, patch_file, temp_path):
                # Hash checking
                sha256_hash = hashlib.sha256()
                with open(temp_path, "rb") as f:
                    for byte_block in iter(lambda: f.read(4096), b""):
                        sha256_hash.update(byte_block)
                
                match = sha256_hash.hexdigest() == original_hash
                os.remove(temp_path) # Cleanup
                return match
            return False
        except:
            if os.path.exists(temp_path): os.remove(temp_path)
            return False
