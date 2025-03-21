import requests

endpoint = "http://0.0.0:8000/users/authority"
token: str = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJVU1ItYjBhMjNmZDgtZDQ2NS00YTQ4LTg3MWItMDhhZjllNmRlMDVjIiwic2NvcGVzIjpbIm93bjpyZWFkIiwib3duOmRlbGV0ZSIsIm93bjp1cGRhdGUiLCJ1c2VyczpsaXN0Il0sImV4cCI6MTc0MjU3MDI1MH0.SB585VpoQKeda6-ajg1sh_ALCHNY4bRgSOvPOn1sbIU"
)
headers = {"Authorization": f"Bearer {token}"}

print(requests.get(endpoint, headers=headers).json())
