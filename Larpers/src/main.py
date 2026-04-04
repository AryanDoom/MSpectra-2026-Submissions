import os
import time
from datetime import datetime
from flask import Flask, send_from_directory, jsonify
from scanner import FileScanner
from database import DatabaseManager, MONGO_AVAILABLE
from ai_classifier import AIClassifier
from garbage_collector import GarbageCollector
from delta_manager import DeltaManager

# --- CONFIGURATION ---
# Set to True to use dummy data for visualization. 
# Set to False to point ASOS at a real local directory.
DEMO_MODE = True
TARGET_DIR = "./data" if DEMO_MODE else "./my_real_project"
# ---------------------

class StorageOptimizationPipeline:
    def __init__(self, target_directory, db_instance=None):
        self.target_directory = target_directory
        self.scanner = FileScanner(target_directory)
        self.db = db_instance if db_instance else DatabaseManager()
        self.classifier = AIClassifier()
        self.gc = GarbageCollector()
        self.delta = DeltaManager() # Tier 3 Optimizer
        self.reclaimed_delta_bytes = 0

    def run(self):
        print("Starting AI-Assisted Storage Optimization Pipeline...")
        
        # 1. Scan directory
        queue = self.scanner.scan_directory()
        
        # 2. Process Files
        print("Processing files and classifying...")
        for file_path in queue:
            if not os.path.exists(file_path):
                continue
                
            metadata = self.scanner.extract_metadata(file_path)
            if not metadata:
                continue
                
            # Two-Tier Deduplication Check
            is_dup = False
            base_file_path = self.db.check_fast_hash(metadata["fast_hash"], metadata["path"])
            
            if base_file_path:
                print(f"  [TIER 1] Fast-hash match for {os.path.basename(file_path)}. Verifying with full hash...")
                full_hash = self.scanner.compute_file_hash(file_path)
                metadata["full_hash"] = full_hash
                
                deep_dup_path = self.db.check_full_hash(full_hash, metadata["path"])
                if deep_dup_path:
                    print(f"  [TIER 2] 100% Duplicate confirmed!")
                    is_dup = True
                else:
                    # Header matches but body doesn't: DELTA CANDIDATE
                    print(f"  [TIER 3] Similar sibling detected. Marking for Delta Compression.")
                    metadata["is_similar_to"] = base_file_path
            
            metadata["is_duplicate"] = is_dup
            
            # AI Classification
            classification = self.classifier.classify(metadata)
            metadata["classification"] = classification
            
            # Save to Database
            self.db.insert_or_update(metadata)
            
            print(f"Processed: {os.path.basename(file_path)} | Class: {classification} | Dup: {is_dup}")
            
        # 3. Garbage Collection
        removable_files = self.db.get_removable_files()
        deleted_count, reclaimed_bytes, removal_details = self.gc.collect(removable_files)
        
        # 3.5 Binary Delta Patching (Tier 3)
        # Find all files marked with 'is_similar_to' that haven't been deleted yet
        similarity_candidates = []
        if not MONGO_AVAILABLE:
            for path, meta in self.db.mock_db.items():
                if meta.get("is_similar_to") and meta.get("status") != "trashed":
                    similarity_candidates.append(meta)
        
        for sim_meta in similarity_candidates:
            target = sim_meta["path"]
            base = sim_meta["is_similar_to"]
            patch_path, savings = self.delta.create_delta(base, target)
            if patch_path:
                # Verify and then "Optimize" (Replace original with patch)
                if self.delta.verify_reconstruction(base, patch_path, sim_meta.get("full_hash")):
                    print(f"✅ Verified Delta for {os.path.basename(target)}. Reducing to Ghost File.")
                    # Move original to trash, update reclaimed counter
                    trash_path = os.path.join(self.gc.trash_dir, f"delta_source_{os.path.basename(target)}")
                    os.replace(target, trash_path)
                    
                    # Update DB to Mark as Ghost/Delta
                    sim_meta["is_delta"] = True
                    sim_meta["patch_path"] = patch_path
                    self.db.mark_as_removed(target, trash_path)
                    
                    self.reclaimed_delta_bytes += savings
                    deleted_count += 1
                else:
                    print(f"❌ Delta verification failed for {target}. Keeping original.")

        # Cleanup DB / Final Update
        for original_path, trash_path in removal_details:
            self.db.mark_as_removed(original_path, trash_path)

            
        # 4. Reporting
        self.generate_report(deleted_count, reclaimed_bytes + self.reclaimed_delta_bytes)
        print("Pipeline execution completed.")
        return {
            "files_scanned": len(queue),
            "deleted_count": deleted_count,
            "reclaimed_bytes": reclaimed_bytes + self.reclaimed_delta_bytes
        }
        
    def generate_report(self, deleted_count, reclaimed_bytes):
        mb_saved = reclaimed_bytes / (1024 * 1024)
        report = f"\n--- Optimization Report ---\n"
        report += f"Files Handled/Trashed: {deleted_count}\n"
        report += f"Storage Reclaimed: {mb_saved:.2f} MB\n"
        report += f"Time: {datetime.now().isoformat()}\n"
        report += "-"*27
        print(report)

app = Flask(__name__, static_folder=None) # Disable default static serving to use our custom one
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@app.route("/")
def intro():
    # Landing Page
    return send_from_directory(ROOT_DIR, "intro.html")

@app.route("/dashboard")
def dashboard():
    # Interactive Simulator
    return send_from_directory(ROOT_DIR, "index.html")

@app.route("/<path:path>")
def serve_assets(path):
    # This route serves style.css, scripts.js, and any other assets
    return send_from_directory(ROOT_DIR, path)

# Initialize a Global Shared Database for this session
shared_db = DatabaseManager()

@app.route("/api/run_pipeline", methods=["POST"])
def api_run_pipeline():
    dummy_target = os.path.abspath(TARGET_DIR)
    
    # Auto-initialize directories (Cloud-Safe)
    try:
        for folder in [dummy_target, "./trash", "./deltas"]:
            if not os.path.exists(folder):
                os.makedirs(folder)
    except OSError:
        print("CRITICAL: Read-Only Filesystem detected. Running in Cloud-Mock Mode.")
            
    if DEMO_MODE:
        print("DEBUG: DEMO_MODE is active. Generating dummy datasets...")
        # 1. Create Active Projects (3 Files x 200MB = 600MB)
        for i in range(3):
            path = os.path.join(dummy_target, f"active_dataset_{i}.idx")
            if not os.path.exists(path):
                with open(path, "wb") as f:
                    f.seek(200 * 1024 * 1024 - 1)
                    f.write(b"\0")
            os.utime(path, (time.time() - 365*2*24*3600, time.time() - 365*2*24*3600))

        # 2. Create Duplicate/Redundant Bloat (3 Files x 100MB = 300MB originally)
        if not os.path.exists(os.path.join(dummy_target, "bloat_file_original.iso")):
            with open(os.path.join(dummy_target, "bloat_file_original.iso"), "wb") as f:
                f.seek(100 * 1024 * 1024 - 1)
                f.write(b"1")
                
        for j in range(2):
            dup_path = os.path.join(dummy_target, f"bloat_file_duplicate_{j}.iso")
            if not os.path.exists(dup_path):
                with open(dup_path, "wb") as f:
                    f.seek(100 * 1024 * 1024 - 1)
                    f.write(b"1")
            os.utime(dup_path, (time.time() - 365*2*24*3600, time.time() - 365*2*24*3600))
                
        # 3. Create Similar Siblings (2 Files x 100MB = 200MB)
        base_sim = os.path.join(dummy_target, "similar_base.bin")
        if not os.path.exists(base_sim):
            with open(base_sim, "wb") as f:
                f.write(b"A" * (1024 * 1024))
                f.write(b"0" * (99 * 1024 * 1024))
                
        variation_sim = os.path.join(dummy_target, "similar_variation.bin")
        if not os.path.exists(variation_sim):
            with open(variation_sim, "wb") as f:
                f.write(b"A" * (1024 * 1024))
                f.write(b"1" * (99 * 1024 * 1024))
        os.utime(variation_sim, (time.time() - 365*2*24*3600, time.time() - 365*2*24*3600))
        
    print(f"DEBUG: api_run_pipeline using target directory: {dummy_target}")
    pipeline = StorageOptimizationPipeline(target_directory=dummy_target, db_instance=shared_db)
    results = pipeline.run()
    
    # Safe Diagnostic Logging
    db_count = len(shared_db.mock_db) if not MONGO_AVAILABLE else "MONGO-LIVE"
    print(f"DEBUG: Pipeline run completed. Database state: {db_count}")
    
    return jsonify({"status": "success", "message": "Pipeline completed", "data": results})

@app.route('/api/restore', methods=['POST'])
def api_restore():
    from flask import request
    data = request.json
    file_path = data.get("path")
    
    # Identify the target directory
    print(f"DEBUG: api_restore using db at {id(shared_db)}")
    dummy_target = os.path.join(ROOT_DIR, "data")
    pipeline = StorageOptimizationPipeline(target_directory=dummy_target, db_instance=shared_db)
    
    # 1. Fetch metadata from "Trashed" history
    # Normalize input path for comparison
    # We strip any trailing .bin (in case of double extensions) and normalize
    clean_file_path = file_path.strip().lower()
    # Handle the weird '.bin.bin' mangling if it happens
    if clean_file_path.endswith(".bin.bin"): clean_file_path = clean_file_path[:-4]
    
    norm_file_path = os.path.normpath(clean_file_path).lower()
    filename_only = os.path.basename(clean_file_path).lower()
    
    # DEBUG: Print DB status
    print(f"DEBUG: Attempting to restore raw input: '{file_path}'")
    print(f"DEBUG: Cleaned/Normalized input: '{norm_file_path}'")
    
    meta = None
    if not MONGO_AVAILABLE:
        trashed_keys = [p for p, m in pipeline.db.mock_db.items() if m.get('status') == 'trashed']
        print(f"DEBUG: MockDB contains {len(pipeline.db.mock_db)} records total.")
        print(f"DEBUG: MockDB trashed basenames: {trashed_keys}")
        
        for path, m in pipeline.db.mock_db.items():
            db_path_norm = os.path.normpath(path).lower()
            db_filename = os.path.basename(path).lower()
            
            # Match if:
            # 1. Exact normalized path match
            # 2. Input path is the basename
            # 3. Input path is contained in the DB path (e.g. 'data/file1' vs 'C:/Code/data/file1')
            if (db_path_norm == norm_file_path or db_filename == filename_only or norm_file_path in db_path_norm) and m.get("status") == "trashed":
                meta = m
                print(f"DEBUG: Match found! Restoring '{path}'")
                break
    else:
        meta = pipeline.db.get_removed_record(file_path)

    if not meta:
        return jsonify({"status": "error", "message": f"No restoration record found for '{file_path}'"}), 404
        
    # 2. Case A: Ghost File (Mathematical Reconstruction)
    if meta.get("is_delta"):
        print(f"Restoring Ghost File via Binary Patch: {file_path}")
        success = pipeline.delta.reconstruct_file(
            meta["is_similar_to"], 
            meta["patch_path"], 
            meta["path"]
        )
    # 3. Case B: Standard Restore (File Move)
    else:
        print(f"Restoring Standard File: {file_path}")
        success = pipeline.gc.restore(meta)
        
    if success:
        # Mark as active again in DB
        meta["status"] = "active"
        meta["trash_path"] = None
        pipeline.db.insert_or_update(meta)
        return jsonify({"status": "success", "message": f"Restored {os.path.basename(file_path)} successfully"})
    else:
        return jsonify({"status": "error", "message": "Restoration failed. Check server logs."}), 500

if __name__ == "__main__":
    print(f"Starting Flask App. Root frontend directory: {ROOT_DIR}")
    # Disable debug mode for final production-stability test
    app.run(host="0.0.0.0", port=5000, debug=False)
