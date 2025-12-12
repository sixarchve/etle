import os, glob
import xml.etree.ElementTree as ET

ANN_DIR = "helmet-detection/annotations"
OUT_DIR = "helmet-detection/labels_yolo"
os.makedirs(OUT_DIR, exist_ok=True)

classes = ["With Helmet", "Without Helmet"]

def to_yolo(w, h, xmin, ymin, xmax, ymax):
    x_c = ((xmin + xmax) / 2.0) / w
    y_c = ((ymin + ymax) / 2.0) / h
    bw  = (xmax - xmin) / w
    bh  = (ymax - ymin) / h
    return x_c, y_c, bw, bh

for xml_path in glob.glob(os.path.join(ANN_DIR, "*.xml")):
    root = ET.parse(xml_path).getroot()

    filename = root.findtext("filename")
    stem = os.path.splitext(filename)[0]

    size = root.find("size")
    w = int(size.findtext("width"))
    h = int(size.findtext("height"))

    lines = []
    for obj in root.findall("object"):
        cls = obj.findtext("name").strip()
        if cls not in classes:
            continue
        cls_id = classes.index(cls)

        b = obj.find("bndbox")
        xmin = float(b.findtext("xmin"))
        ymin = float(b.findtext("ymin"))
        xmax = float(b.findtext("xmax"))
        ymax = float(b.findtext("ymax"))

        x_c, y_c, bw, bh = to_yolo(w, h, xmin, ymin, xmax, ymax)
        lines.append(f"{cls_id} {x_c:.6f} {y_c:.6f} {bw:.6f} {bh:.6f}")

    with open(os.path.join(OUT_DIR, f"{stem}.txt"), "w") as f:
        f.write("\n".join(lines))
