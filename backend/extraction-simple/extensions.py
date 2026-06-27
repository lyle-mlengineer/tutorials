from tubectrl import YouTube


credentials_path: str = "/home/lyle/.youtube/credentials.json"
youtube = YouTube()
youtube.authenticate_from_credentials(credentials_path=credentials_path)