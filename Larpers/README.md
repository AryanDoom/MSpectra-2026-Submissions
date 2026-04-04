# Submission: Team Larpers (ASOS v4.1.0)

## Team Details
- **Team Name**: Larpers
- **Team Members**: 
  - Aryan Shukla
  - Shaurya Pandey
  - Tejaswi

##  Assigned Problem Statement
**Company**: Microsoft
**Problem Statement**: Building an AI-assisted system to combat data redundancy in massive, high-throughput file systems.

---

# ASOS: AI-Assisted Storage Optimization System
ASOS is a high-performance optimization engine designed to reclaim disk space through **Multi-Tier Deduplication**, **Binary Delta Compression (Tier 3)**, and **Heuristic AI Classification**. Unlike standard cleanup tools, ASOS can reduce the footprint of unique but similar files (e.g., daily database backups or multiple versions of the same ISO) by up to 99%.

##  Architectural Deep-Dive

ASOS operates on a 4-phase technical optimization pipeline:

### 1. The Multi-Tier Scanning Engine
To ensure speed on massive file systems (100GB+), ASOS avoids full SHA-256 computation on every file:
*   **Tier 1 (Fast Fingerprinting)**: Computes a hash of only the **first 1MB** of header data. This acts as a high-speed filter to identify potential duplicates without full-disk read-latency.
*   **Tier 2 (Cryptographic Verification)**: If a fast-hash collision is detected, ASOS performs a full **SHA-256** scan. If the full hashes match, the files are 100% bit-identical clones.

### 2. Tier 3: Binary Delta Compression (Ghost Files)
When two files share the same 1MB header but have different full hashes (e.g., `Update_v1.iso` and `Update_v2.iso`), ASOS recognizes them as **"Similar Siblings"**.
*   **bsdiff4 Algorithm**: ASOS uses the `bsdiff4` binary diffing algorithm to calculate the mathematical difference between the "Base" file and the "Variation."
*   **Ghost File Creation**: THE variation is substituted with a tiny **Binary Patch** (delta). This reduces a 100MB file to a ~10KB patch while keeping it mathematically reconstructible bit-for-bit.

### 3. AI-Assisted Classification
Every file is graded across **6 dimensions** to determine its "Dead Weight" status:
*   **Temporal Decay**: Days since last access vs. creation date.
*   **Structural Depth**: Files buried deep in system/temp directories are prioritized for optimization.
*   **Semantic Keywords**: Detection of terms like `backup`, `old`, `copy`, and `final` in file paths.
*   **Inference**: Uses a `RandomForestClassifier` (serialized in `models/`) to predict if a file is `Redundant`, `Important`, or `Archive`.

### 4. Non-Destructive Restoration Engine
*   **Safety First**: ASOS never permanently deletes data. Files are moved to a timestamped, indexed `/trash` directory.
*   **Mathematical Reconstruction**: Optimized "Ghost Files" are physically reconstructed by applying the stored patch back onto the Base file using the `bsdiff4` patching engine.

##  Tech Stack
- **Backend / Engine**: Python 3.10+
- **Web Framework**: Flask (RESTful API & Controller)
- **Binary Intelligence**: `bsdiff4` (Binary Delta Engine)
- **AI / Machine Learning**: Scikit-Learn (`RandomForestClassifier`)
- **Hashing**: SHA-256 (via `hashlib`)
- **Frontend**: HTML5, CSS3 (Vanilla), JavaScript (ES6)

---

###  How to Run locally
1.  **Install Requirements**:
    ```bash
    pip install -r Larpers/requirements.txt
    ```
2.  **Launch the System**:
    ```bash
    python Larpers/src/main.py
    ```
3.  **Access Dashboard**: Open `http://localhost:5000` to run the integrated simulator.

###  Build & Restoration
Optimized files are moved to the `/trash` quarantine. Users can restore any file instantly via the mathematical reconstruction engine built into the dashboard.
