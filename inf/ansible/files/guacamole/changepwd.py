import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8080/guacamole"


def getToken(password):
    # Post /api/tokens with username and password
    url = BASE_URL + "/api/tokens"
    headers = {}
    data = {"username": "guacadmin", "password": password}
    response = requests.post(url, headers=headers, data=data)
    token = response.json()["authToken"]
    return token

token = getToken()

def changePwd(old,new):
    url = BASE_URL + "/api/session/data/mysql/users/guacadmin/password?token=" + token
    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "oldPassword": old,
        "newPassword": new
    }
    response = requests.put(url, headers=headers, data=json.dumps(data))
    print(response.status_code)
    print(response.text)

old_password = sys.argv[1]
new_password = sys.argv[2]
