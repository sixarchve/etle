# ETLE – Helmet Violation Detection (ETL Project)

This project implements a **helmet violation detection system** inspired by e-Tilang, designed as a **final project for the Data Processing & Data Infrastructure course**.

The system applies an **ETL (Extract–Transform–Load)** approach to process:

* **Unstructured data**: CCTV video streams and image evidence
* **Structured data**: violation metadata stored in a relational database

---

## 📌 Project Overview

**Goal:**
Detect motorcycle riders **not wearing helmets**, generate evidence, and store structured violation data for analysis and reporting.

**Core idea:**
Computer vision (YOLO + tracking) is used as the **Transform** stage in an ETL pipeline.

---

## 🏗️ ETL Architecture

### 1. Extract

* Source: CCTV video (`video/*.mp4`)
* Frames are extracted in real time using OpenCV.

### 2. Transform

* YOLO object detection + ByteTrack tracking
* Sliding window voting to reduce false positives
* When a violation is confirmed:

  * Evidence image is saved
  * Metadata is generated as JSON

### 3. Load

* A separate loader script reads metadata JSON files
* Data is inserted into PostgreSQL
* Duplicate loads are prevented (idempotent design)

---

## 📂 Project Structure

```
etle/
├── video.py                # Transform: detection + event generation
├── loader.py               # Load: JSON → PostgreSQL
├── docker-compose.yaml     # PostgreSQL service
├── database/
│   └── init_db.sql         # Database schema
├── output/                 # Generated events (ignored by git)
│   └── <event_id>/
│       ├── evidence.jpg
│       └── metadata.json
├── requirements.txt
├── data.yaml               # YOLO dataset config
└── .gitignore
```

---

## 🗄️ Database Design

**Database:** PostgreSQL
**Table:** `helmet_violations`

Each record represents **one confirmed violation**, including:

* Event ID (UUID)
* Camera ID
* Track ID
* Violation type
* Confidence ratio
* Timestamp
* Evidence path
* Raw metadata (JSONB)

Schema is defined in:

```
database/init_db.sql
```

---

## 🚀 How to Run (Quick Start)

### 1️⃣ Start PostgreSQL

```bash
docker compose up -d
```

### 2️⃣ Initialize database

Open DBeaver and run:

```sql
database/init_db.sql
```

### 3️⃣ Run Transform (generate events)

```bash
python video.py
```

This creates:

```
output/<event_id>/
  ├── evidence.jpg
  └── metadata.json
```

### 4️⃣ Run Load (insert into database)

```bash
python loader.py
```

---

## 🔁 ETL Characteristics

* Batch-oriented ETL
* Separation of Transform and Load
* Idempotent loading
* Auditable evidence storage
* Scalable design (can be extended to Kafka / S3)

---

## 🧠 Technologies Used

* Python 3.12
* OpenCV
* Ultralytics YOLO
* ByteTrack
* PostgreSQL
* Docker / Docker Compose
* psycopg (PostgreSQL driver)

---

## 📚 Academic Notes

This project demonstrates:

* Practical ETL implementation
* Handling unstructured → structured data
* Real-world data engineering concepts
* Reproducible and modular pipeline design

---

## ✍️ Author

**Name:** Aether
**Course:** Data Processing & Infrastructure
**Project Type:** Final Assignment
