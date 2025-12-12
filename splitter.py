import os, random, shutil, glob

IMG_DIR = "helmet-detection/images"
LBL_DIR = "helmet-detection/labels_yolo"

OUT = "helmet-dataset"
for p in [f"{OUT}/images/train", f"{OUT}/images/val", f"{OUT}/labels/train", f"{OUT}/labels/val"]:
    os.makedirs(p, exist_ok=True)

imgs = []
for ext in ("*.jpg","*.jpeg","*.png"):
    imgs += glob.glob(os.path.join(IMG_DIR, ext))

random.seed(42)
random.shuffle(imgs)
cut = int(0.8 * len(imgs))
train, val = imgs[:cut], imgs[cut:]

def copy_pair(img_path, split):
    stem = os.path.splitext(os.path.basename(img_path))[0]
    lbl_path = os.path.join(LBL_DIR, stem + ".txt")
    if not os.path.exists(lbl_path):
        return
    shutil.copy2(img_path, f"{OUT}/images/{split}/{os.path.basename(img_path)}")
    shutil.copy2(lbl_path, f"{OUT}/labels/{split}/{stem}.txt")

for p in train: copy_pair(p, "train")
for p in val:   copy_pair(p, "val")

print("done:", len(train), "train,", len(val), "val")
