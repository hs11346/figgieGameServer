import requests
import threading
import json
import re
import pandas as pd

url = "http://127.0.0.1:5000"
user = None
name = input("Input your username: ")


def update_polling(url):
    cache = []
    while True:
        r = requests.get(url + "/updates")
        if r.status_code == 200:
            updates = json.loads(r.content)
            if updates == cache:
                continue
            else:
                print(pd.DataFrame([i for i in updates if i not in cache]))
                cache = updates
        else:
            print("ERROR CODE {}: {}".format(r.status_code, r.content))

x = threading.Thread(target=update_polling, args=(url,))
x.start()

while True:
    command = input("")
    if command.startswith("join"):
        r = requests.post(url+"/join", json={"username": name})
        if r.status_code == 200:
            user = json.loads(r.content)
            print(user)
        else:
            print("ERROR CODE {}: {}".format(r.status_code, r.content))
    if command.startswith("start"):
        r = requests.post(url + "/start", json={"status": "start"})
        if r.status_code == 200:
            print(r.content)
            r = requests.get(url + f"/{user['id']}/hand")
            print(r.content)
        else:
            print("ERROR CODE {}: {}".format(r.status_code, r.content))
    if command.startswith("orderbook"):
        r = requests.get(url + "/orderbookSnapshot")
        if r.status_code == 200:
            print(r.content)
        else:
            print("ERROR CODE {}: {}".format(r.status_code, r.content))
    if command.startswith("wallet"):
        r = requests.get(url + f"/{user['id']}/accessWallet")
        if r.status_code == 200:
            print(r.content)
        else:
            print("ERROR CODE {}: {}".format(r.status_code, r.content))
    if command.startswith("leaderboard"):
        r = requests.get(url + "/chipleaderboard")
        if r.status_code == 200:
            print(json.loads(r.content))
        else:
            print("ERROR CODE {}: {}".format(r.status_code, r.content))
    if command.startswith("quote"):
        command, suit, price, direction = command.split(",")
        price = int(price)
        r = requests.post(url + f"/{user['id']}/submitQuote", json={
            "suit": suit,
            "price" : price,
            "direction": direction
        })
        if r.status_code == 200:
            print(json.loads(r.content))
            r = requests.get(url + f"/{user['id']}/hand")
            print(json.loads(r.content))
        else:
            print("ERROR CODE {}: {}".format(r.status_code, r.content))
    if command.startswith("trade"):
        command, suit, direction = command.split(",")
        r = requests.post(url + f"/{user['id']}/submitTrade", json={
            "suit": suit,
            "direction": direction
        })
        if r.status_code == 200:
            print(json.loads(r.content))
            r = requests.get(url + f"/{user['id']}/hand")
            print(json.loads(r.content))
        else:
            print("ERROR CODE {}: {}".format(r.status_code, r.content))
