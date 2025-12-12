import cv2
from ultralytics import YOLO
import os

VIDEO_PATH = "video/h2.mp4"
MODEL_PATH = "runs/detect/train/weights/best.pt"
OUT_PATH = "video/output/output_annotated.mp4"

model = YOLO(MODEL_PATH)

cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    raise SystemExit(f"❌ Cannot open video: {VIDEO_PATH}")

fps = cap.get(cv2.CAP_PROP_FPS) or 25
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

fourcc = cv2.VideoWriter_fourcc(*"mp4v")
writer = cv2.VideoWriter(OUT_PATH, fourcc, fps, (w, h))

print("✅ Running detection... press Q to stop preview.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, conf=0.7, verbose=False)

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            if cls_id == 1:  # Without Helmet
                label = f"NO HELMET {conf:.2f}"
                color = (0, 0, 255)
            else:            # With Helmet
                label = f"HELMET {conf:.2f}"
                color = (0, 255, 0)

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, max(20, y1 - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    writer.write(frame)

    cv2.imshow("Helmet Detection (Video)", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
writer.release()
cv2.destroyAllWindows()

print(f"✅ Saved annotated video to: {os.path.abspath(OUT_PATH)}")
