import os
from PIL.DdsImagePlugin import item
from datasets import load_dataset
import PIL
import uuid

# 1. Load your dataset from the Hugging Face Hub
snapshot_dir = "/home/lyle/.cache/huggingface/hub/datasets--lyle-mlengineer--kenyan-celeb-faces/snapshots/50ec8c741889b78081756939651447bbbbc12a2c"
ds = load_dataset("parquet", data_dir=snapshot_dir)

base_output_dir = "/home/lyle/datasets/images/kenyan-celeb-faces-original"

for split in ["train", "test", "validation"]:
    dataset_split = ds[split]
    split_output_dir = os.path.join(base_output_dir, split)
    os.makedirs(split_output_dir, exist_ok=True)

    for item in dataset_split:
        image = item["image"]  # This yields a PIL Image object
        label = item["label"]  # This yields the class label
        
        image_name = f"{uuid.uuid4()}.jpg"  # Generate a unique filename
        output_path = os.path.join(split_output_dir, image_name)
        
        image.save(output_path, format="JPEG")  # Save the image in JPEG format
        print(f"Saved image to {output_path} with label {label}")