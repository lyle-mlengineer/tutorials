import requests

endpoint = "http://0.0.0:8000/users/me"
token: str = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJVU1ItYjBhMjNmZDgtZDQ2NS00YTQ4LTg3MWItMDhhZjllNmRlMDVjIiwic2NvcGVzIjpbIm93bjpyZWFkIiwib3duOmRlbGV0ZSIsIm93bjp1cGRhdGUiLCJ1c2VyczpsaXN0Il0sImV4cCI6MTc0MjU2NjA0Mn0.J0Ok3S6lazPkEvi4v1yNTuxZkxq7wHwJto4CeT96jg0"
)
headers = {"Authorization": f"Bearer {token}"}

print(requests.get(endpoint, headers=headers).json())
