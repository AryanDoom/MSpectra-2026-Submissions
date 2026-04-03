# Submission: Team Larpers

## 📌 Team Details
- **Team Name**: Larpers
- **Team Members**: 
  - Aryan Shukla
  - Shaurya
  - Tejaswi

## 🏢 Assigned Problem Statement
**Company**: Microsoft
**Problem Statement**: Building an AI-assisted system to combat data redundancy in massive, high-throughput file systems.

## 🧠 Project Overview: ASOS (AI-Assisted Storage Optimization System)
ASOS is a high-performance optimization engine that uses **Binary Delta Compression (Tier 3)** and **Heuristic AI Classification** to reclaim up to 99% of space in redundant datasets. 

It solves the redundancy problem through a 4-phase technical pipeline:
1.  **Header Fingerprinting (Tier 1)**: Rapid scanning for potential duplicates using SHA-256 on the first 1MB of file data.
2.  **SHA-256 Deduplication (Tier 2)**: Full bit-for-bit verification to identify identical clones across the filesystem.
3.  **Binary Delta Patching (Tier 3)**: Utilizing the `bsdiff4` algorithm to turn similar sibling files into tiny 10KB patches (Ghost Files).
4.  **AI Classification Engine**: A 6-dimension heuristic grading system (using Scikit-Learn) to automatically identify "Dead Weight" data based on access patterns and semantic metadata.

## 🛠️ Tech Stack
- **Backend / Engine**: Python 3.10+
- **Web Framework**: Flask (RESTful API & Controller)
- **Binary Intelligence**: bsdiff4 (Binary Delta Engine)
- **AI / Machine Learning**: Scikit-Learn (RandomForestClassifier)
- **Hashing**: SHA-256 (via hashlib)
- **Frontend**: HTML5, CSS3 (Vanilla), JavaScript (ES6)

---
### 🚀 How to Run locally
1.  `pip install -r Larpers/requirements.txt`
2.  `python Larpers/src/main.py`
3.  Access the dashboard at `http://localhost:5000`

### 🔧 Build & Restoration
Optimized files are moved to the `/trash` quarantine. Users can restore any file instantly via the mathematical reconstruction engine built into the dashboard.
