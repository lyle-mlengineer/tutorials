from routers.schemas import FileReadResponse, FileWriteResponse
from core.config import Settings

OUTPUT_DIR = Settings().OUTPUT_DIR
DATA_DIR = Settings().DATA_DIR

def write_file(name, content):
    file_name = f"{name}.txt"
    file_path = f"{OUTPUT_DIR}/{file_name}"
    with open(file_path, "w") as f:
        f.write(content)
    return FileWriteResponse(file_path=file_path)

def read_file(file_name):
    file_name = f"{file_name}.txt"
    file_path = f"{OUTPUT_DIR}/{file_name}"
    with open(file_path, "r") as f:
        content = f.read()
    return FileReadResponse(content=content)

def write_data(name, content):
    file_name = f"{name}_data.txt"
    file_path = f"{DATA_DIR}/{file_name}"
    with open(file_path, "w") as f:
        f.write(content)
    return FileWriteResponse(file_path=file_path)