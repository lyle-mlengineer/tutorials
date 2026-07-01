import os
from PIL.DdsImagePlugin import item
from datasets import load_dataset
import PIL
import uuid

# 1. Load your dataset from the Hugging Face Hub
snapshot_dir = "/home/lyle/.cache/huggingface/hub/datasets--lyle-mlengineer--kenyan-celeb-faces/snapshots/50ec8c741889b78081756939651447bbbbc12a2c"
ds = load_dataset("parquet", data_dir=snapshot_dir)

base_output_dir = "/home/lyle/datasets/images/kenyan-celeb-faces-original"

# for split in ["train", "test", "validation"]:
#     dataset_split = ds[split]
#     split_output_dir = os.path.join(base_output_dir, split)
#     os.makedirs(split_output_dir, exist_ok=True)

#     for item in dataset_split:
#         image = item["image"]  # This yields a PIL Image object
#         label = item["label"]  # This yields the class label
        
#         image_name = f"{uuid.uuid4()}.jpg"  # Generate a unique filename
#         output_path = os.path.join(split_output_dir, image_name)
        
#         image.save(output_path, format="JPEG")  # Save the image in JPEG format
#         print(f"Saved image to {output_path} with label {label}")

IMAGE_DATA_PATH: str = "/home/lyle/datasets/images"
CELEB_FACES_PATH: str = os.path.join(IMAGE_DATA_PATH, "kenyan-celeb-faces")
for split in os.listdir(CELEB_FACES_PATH):
    split_path = os.path.join(CELEB_FACES_PATH, split)
    if os.path.isdir(split_path):
        for image_file in os.listdir(split_path):
            image_path = os.path.join(split_path, image_file)
            destination_path = os.path.join(base_output_dir, split, image_file)
            # copy image
            image = PIL.Image.open(image_path)
            image.save(destination_path, format="JPEG")
            print(f"Saved image to {destination_path}")