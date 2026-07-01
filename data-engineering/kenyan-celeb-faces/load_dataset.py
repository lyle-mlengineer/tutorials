from datasets import load_dataset
from dotenv import load_dotenv
import os
import uuid
import random

load_dotenv(".env")
IMAGE_DATA_PATH: str = "/home/lyle/datasets/images"
CELEB_FACES_PATH: str = os.path.join(IMAGE_DATA_PATH, "kenyan-celeb-faces")
DATASET_NAME: str = "lyle-mlengineer/kenyan-celeb-faces"
RAW_IMAGES_PATH: str = os.path.join(IMAGE_DATA_PATH, "raw")
CHOICES: list = ["train", "test", "validation"]

def move_images_to_dataset_folder(split: str = "train") -> None:
    """
    Move images from the raw folder to the dataset folder.
    """
    if not os.path.exists(RAW_IMAGES_PATH):
        print(f"Raw images path {RAW_IMAGES_PATH} does not exist.")
        return

    if not os.path.exists(CELEB_FACES_PATH):
        os.makedirs(CELEB_FACES_PATH)

    for filename in os.listdir(RAW_IMAGES_PATH):  # Limit to first 10 files for testing
        if filename.endswith(".jpg") or filename.endswith(".png"):
            split = random.choices(CHOICES, weights=[0.8, 0.1, 0.1], k=1)[0]  # Randomly assign to train, test, or validation
            src_path = os.path.join(RAW_IMAGES_PATH, filename)
            file_extension = os.path.splitext(filename)[1]
            new_filename = f"{uuid.uuid4()}{file_extension}"
            dst_path = os.path.join(CELEB_FACES_PATH, split, new_filename)
            os.rename(src_path, dst_path)
            print(f"Moved {src_path} to {dst_path}")

    print(f"Moved {len(os.listdir(RAW_IMAGES_PATH))} images to {CELEB_FACES_PATH}")


move_images_to_dataset_folder()

dataset = load_dataset("imagefolder", data_dir=CELEB_FACES_PATH)
print(dataset)
dataset.push_to_hub(DATASET_NAME, token=os.environ.get('HF_WRITE_TOKEN', None))