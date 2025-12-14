import cv2
from ultralytics import YOLO
import os, json, uuid
from datetime import datetime
from collections import deque, defaultdict

VIDEO_PATH = "video/cctv.mp4"
MODEL_PATH = "runs/detect/train/weights/best.pt"

SAVE_DIR = "output"
os.makedirs(SAVE_DIR, exist_ok=True)

CAMERA_ID = "cctv"
TRACKER_CFG = "bytetrack.yaml"

WINDOW_SIZE = 15
ENTER_RATIO = 0.8

hist = defaultdict(lambda: deque(maxlen=WINDOW_SIZE))
state_nohelmet = set()
saved_ids = set()

model = YOLO(MODEL_PATH)

cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    raise SystemExit(f"❌ Cannot open video: {VIDEO_PATH}")

fps = cap.get(cv2.CAP_PROP_FPS) or 25
print(f"✅ Transform running... FPS={fps:.2f} | press Q to stop preview.")

frame_idx = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame_idx += 1

    results = model.track(
        frame,
        conf=0.25,
        iou=0.5,
        tracker=TRACKER_CFG,
        persist=True,
        verbose=False
    )

    r = results[0]
    frame_annotated = frame.copy()
    seen_ids = set()

    if r.boxes is not None and len(r.boxes) > 0:
        ids = r.boxes.id

        for i, box in enumerate(r.boxes):
            cls_id = int(box.cls[0])          # your dataset: 1 = no-helmet
            det_conf = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            track_id = int(ids[i]) if ids is not None else -1
            if track_id == -1:
                continue

            seen_ids.add(track_id)

            # 1=nohelmet, 0=helmet/ok
            hist[track_id].append(1 if cls_id == 1 else 0)
            ratio = sum(hist[track_id]) / len(hist[track_id])

            # lock when stable
            if (
                track_id not in state_nohelmet and
                len(hist[track_id]) == WINDOW_SIZE and
                ratio >= ENTER_RATIO
            ):
                state_nohelmet.add(track_id)

            # draw
            if track_id in state_nohelmet:
                label = f"ID {track_id} | NO HELMET (LOCKED) {ratio:.2f}"
                color = (0, 0, 255)
            else:
                label = f"ID {track_id} | HELMET/OK {ratio:.2f}"
                color = (0, 255, 0)

            cv2.rectangle(frame_annotated, (x1, y1), (x2, y2), color, 2)
            cv2.putText(
                frame_annotated,
                label,
                (x1, max(20, y1 - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2
            )

            # Save once per track_id (same as your logic)
            if track_id in state_nohelmet and track_id not in saved_ids:
                ts = datetime.now()
                event_id = str(uuid.uuid4())

                # event folder
                event_dir = os.path.join(SAVE_DIR, event_id)
                os.makedirs(event_dir, exist_ok=True)

                # file names inside folder
                img_filename = "evidence.jpg"
                json_filename = "metadata.json"
                img_path = os.path.join(event_dir, img_filename)
                json_path = os.path.join(event_dir, json_filename)

                # save evidence image (annotated)
                cv2.imwrite(img_path, frame_annotated)

                # build metadata
                metadata = {
                    "event_id": event_id,
                    "camera_id": CAMERA_ID,
                    "track_id": track_id,
                    "violation_type": "NO_HELMET",
                    "confidence_ratio": round(ratio, 3),
                    "frame_index": frame_idx,
                    "timestamp": ts.isoformat(),
                    "evidence_image": img_filename,
                    # NOTE: loader.py will derive evidence_path from folder;
                    # you can include it too if you want:
                    # "evidence_path": img_path,
                    "source_video": VIDEO_PATH,
                    "model_path": MODEL_PATH,
                    "det_conf": round(det_conf, 3),
                    "window_size": WINDOW_SIZE,
                    "enter_ratio": ENTER_RATIO
                }

                # save metadata.json
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)

                print(f"📁 Event created: {event_dir}")
                saved_ids.add(track_id)

    # cleanup old IDs
    for tid in list(hist.keys()):
        if tid not in seen_ids:
            hist.pop(tid, None)

    cv2.imshow("Transform (YOLO + Track + Vote)", frame_annotated)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
print("✅ Transform finished.")
