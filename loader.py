import os
import json
import psycopg
from pathlib import Path

# ---- CONFIG ----
OUTPUT_DIR = "output"
PG_DSN = "postgresql://etle:etlepass@localhost:5432/etle_db"

INSERT_SQL = """
INSERT INTO helmet_violations (
  event_id, camera_id, track_id, violation_type,
  confidence_ratio, frame_index, event_time,
  evidence_image, evidence_path, source_video, model_path,
  det_conf, window_size, enter_ratio, raw_json
)
VALUES (
  %(event_id)s::uuid, %(camera_id)s, %(track_id)s, %(violation_type)s,
  %(confidence_ratio)s, %(frame_index)s, %(event_time)s,
  %(evidence_image)s, %(evidence_path)s, %(source_video)s, %(model_path)s,
  %(det_conf)s, %(window_size)s, %(enter_ratio)s, %(raw_json)s::jsonb
)
ON CONFLICT (event_id) DO NOTHING;
"""

def load_events():
    with psycopg.connect(PG_DSN) as conn:
        with conn.cursor() as cur:
            for event_dir in Path(OUTPUT_DIR).iterdir():
                if not event_dir.is_dir():
                    continue

                meta_path = event_dir / "metadata.json"
                evidence_path = event_dir / "evidence.jpg"
                loaded_flag = event_dir / "loaded.ok"

                # skip if already loaded
                if loaded_flag.exists():
                    continue

                if not meta_path.exists():
                    print(f"⚠️  Missing metadata.json in {event_dir}")
                    continue

                with open(meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)

                params = {
                    "event_id": meta["event_id"],
                    "camera_id": meta["camera_id"],
                    "track_id": meta["track_id"],
                    "violation_type": meta["violation_type"],
                    "confidence_ratio": meta["confidence_ratio"],
                    "frame_index": meta["frame_index"],
                    "event_time": meta["timestamp"],
                    "evidence_image": meta["evidence_image"],
                    "evidence_path": str(evidence_path),
                    "source_video": meta["source_video"],
                    "model_path": meta["model_path"],
                    "det_conf": meta["det_conf"],
                    "window_size": meta["window_size"],
                    "enter_ratio": meta["enter_ratio"],
                    "raw_json": json.dumps(meta),
                }

                cur.execute(INSERT_SQL, params)
                conn.commit()

                # mark as loaded
                loaded_flag.write_text("ok\n")

                print(f"🗄️ Loaded event {meta['event_id']}")

if __name__ == "__main__":
    load_events()
