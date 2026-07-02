from oryks_google_drive import GoogleDrive
from oryks_google_drive.mime_types import MimeType
import json

def save_resource(resource: dict, resource_name: str) -> None:
    resource_name = f'{resource_name}.json'
    with open(resource_name, 'w') as f:
        json.dump(resource, fp=f, indent=4)


def load_resource(resource_path: str) -> dict:
    with open(resource_path, 'r') as f:
        return json.load(f)


client_secrets_file = "/home/lyle/secrets/drive.json"
drive = GoogleDrive()
drive.authenticate(client_secrets_file)