import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8080/guacamole"


def getToken():
    # Post /api/tokens with username and password
    url = BASE_URL + "/api/tokens"
    headers = {}
    data = {"username": "guacadmin", "password": "guacadmin"}
    response = requests.post(url, headers=headers, data=data)
    token = response.json()["authToken"]
    return token


def createRDPConnection(token, host, port, user, password):
    # Post /api/session/data/postgresql with token and connection parameters
    url = BASE_URL + "/api/session/data/mysql/connections?token=" + token
    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "parentIdentifier": "ROOT",
        "name": host,
        "protocol": "rdp",
        "parameters": {
            "port": port,
            "read-only": "",
            "swap-red-blue": "",
            "cursor": "",
            "color-depth": "",
            "clipboard-encoding": "",
            "disable-copy": "",
            "disable-paste": "",
            "dest-port": "",
            "recording-exclude-output": "",
            "recording-exclude-mouse": "",
            "recording-include-keys": "",
            "create-recording-path": "",
            "enable-sftp": "",
            "sftp-port": "",
            "sftp-server-alive-interval": "",
            "enable-audio": "",
            "security": "",
            "disable-auth": "",
            "ignore-cert": "true",
            "gateway-port": "",
            "server-layout": "",
            "timezone": "",
            "console": "",
            "width": "",
            "height": "",
            "dpi": "",
            "resize-method": "",
            "console-audio": "",
            "disable-audio": "",
            "enable-audio-input": "",
            "enable-printing": "",
            "enable-drive": "",
            "create-drive-path": "",
            "enable-wallpaper": "",
            "enable-theming": "",
            "enable-font-smoothing": "",
            "enable-full-window-drag": "",
            "enable-desktop-composition": "",
            "enable-menu-animations": "",
            "disable-bitmap-caching": "",
            "disable-offscreen-caching": "",
            "disable-glyph-caching": "",
            "preconnection-id": "",
            "hostname": host,
            "username": user,
            "password": password,
            "domain": "",
            "gateway-hostname": "",
            "gateway-username": "",
            "gateway-password": "",
            "gateway-domain": "",
            "initial-program": "",
            "client-name": "",
            "printer-name": "",
            "drive-name": "",
            "drive-path": "",
            "static-channels": "",
            "remote-app": "",
            "remote-app-dir": "",
            "remote-app-args": "",
            "preconnection-blob": "",
            "load-balance-info": "",
            "recording-path": "",
            "recording-name": "",
            "sftp-hostname": "",
            "sftp-host-key": "",
            "sftp-username": "",
            "sftp-password": "",
            "sftp-private-key": "",
            "sftp-passphrase": "",
            "sftp-root-directory": "",
            "sftp-directory": "",
        },
        "attributes": {
            "max-connections": "",
            "max-connections-per-user": "",
            "weight": "",
            "failover-only": "",
            "guacd-port": "",
            "guacd-encryption": "",
            "guacd-hostname": "",
        },
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()


def createSSHConnection(token, host, port, user, private):
    # Post /api/session/data/postgresql with token and connection parameters
    url = BASE_URL + "/api/session/data/mysql/connections?token=" + token
    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "parentIdentifier": "ROOT",
        "name": host,
        "protocol": "ssh",
        "parameters": {
            "port": port,
            "read-only": "",
            "swap-red-blue": "",
            "cursor": "",
            "color-depth": "",
            "clipboard-encoding": "",
            "disable-copy": "",
            "disable-paste": "",
            "dest-port": "",
            "recording-exclude-output": "",
            "recording-exclude-mouse": "",
            "recording-include-keys": "",
            "create-recording-path": "",
            "enable-sftp": "",
            "sftp-port": "",
            "sftp-server-alive-interval": "",
            "enable-audio": "",
            "color-scheme": "",
            "font-size": "",
            "scrollback": "",
            "timezone": None,
            "server-alive-interval": "",
            "backspace": "",
            "terminal-type": "",
            "create-typescript-path": "",
            "hostname": host,
            "host-key": "",
            "private-key": private,
            "username": user,
            "password": "",
            "passphrase": "",
            "font-name": "",
            "command": "",
            "locale": "",
            "typescript-path": "",
            "typescript-name": "",
            "recording-path": "",
            "recording-name": "",
            "sftp-root-directory": "",
        },
        "attributes": {
            "max-connections": "",
            "max-connections-per-user": "",
            "weight": "",
            "failover-only": "",
            "guacd-port": "",
            "guacd-encryption": "",
            "guacd-hostname": "",
        },
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()


token = getToken()

if sys.argv[1] == "rdp":
    print(createRDPConnection(token, sys.argv[2], "3389", "administrator", sys.argv[3]))
elif sys.argv[1] == "ssh":
    print(createSSHConnection(token, sys.argv[2], "22", "ubuntu", sys.argv[3]))
