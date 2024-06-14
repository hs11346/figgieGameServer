import streamlit as st
import requests
import threading
import json
import re
import pandas as pd
import time
st.set_page_config(layout="wide")
st.title("Figgie Game GUI by HARRY")
st.markdown("This GUI is used to conncet to the Figgie API endpoints. It allows you to write bots to algotrade, while this GUI is meant for human use.")
# spades, hearts, clubs, diamonds = st.columns(4)
# with spades:
#     st.header("Spades")
#     spade_px = st.empty()
# with hearts:
#     st.header("hearts")
#     heart_px = st.empty()
# with clubs:
#     st.header("clubs")
#     club_px = st.empty()
# with diamonds:
#     st.header("diamonds")
#     diamond_px = st.empty()

t1, t2 = st.tabs(["start",'trading monitor'])

with t1:
    st.header("Live updates from server")
    live_update_container = st.empty()
    container = st.container()

with t2:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Market State")
        seconds = st.empty()
        url = "http://127.0.0.1:5000"
        orderbook = st.empty()
    with col2:
        st.header("You account")
        wallet = st.empty()
        st.markdown("hand")
        hand = st.empty()
    with col3:
        st.header("Market Updates")
        update_board = st.empty()

    st.header("Results from last game")
    results = st.empty()

    command = st.text_input("Enter Command", "Here")
    command_output_field = st.empty()

    if command == 'user':
        with command_output_field.container():
            st.write(st.session_state["user"])
    if command.startswith("join"):
        command,name = command.split(",")
        r = requests.post(url + "/join", json={"username": name})
        st.session_state["user"] = json.loads(r.content)
        if r.status_code == 200:
            with command_output_field.container():
                st.write(st.session_state["user"])
        else:
            print("ERROR CODE {}: {}".format(r.status_code, r.content))
    if command.startswith("start"):
        r = requests.post(url + "/start", json={"status": "start"})
        if r.status_code == 200:
            r = requests.get(url + f"/{st.session_state['user']['id']}/hand")
            with command_output_field.container():
                st.write(r.content)
        else:
            print("ERROR CODE {}: {}".format(r.status_code, r.content))
    if command.startswith("orderbook"):
        r = requests.get(url + "/orderbookSnapshot")
        if r.status_code == 200:
            with command_output_field.container():
                st.write(r.content)
        else:
            print("ERROR CODE {}: {}".format(r.status_code, r.content))
    if command.startswith("wallet"):
        r = requests.get(url + f"/{st.session_state['user']['id']}/accessWallet")
        if r.status_code == 200:
            with command_output_field.container():
                st.write(r.content)
        else:
            print("ERROR CODE {}: {}".format(r.status_code, r.content))
    if command.startswith("leaderboard"):
        r = requests.get(url + "/chipleaderboard")
        if r.status_code == 200:
            with command_output_field.container():
                st.write(json.loads(r.content))

        else:
            print("ERROR CODE {}: {}".format(r.status_code, r.content))
    if command.startswith("quote"):
        command, suit, price, direction = command.split(",")
        price = int(price)
        r = requests.post(url + f"/{st.session_state['user']['id']}/submitQuote", json={
            "suit": suit,
            "price": price,
            "direction": direction
        })
        if r.status_code == 200:
            with command_output_field.container():
                st.write(json.loads(r.content))
        else:
            print("ERROR CODE {}: {}".format(r.status_code, r.content))
    if command.startswith("trade"):
        command, suit, direction = command.split(",")
        r = requests.post(url + f"/{st.session_state['user']['id']}/submitTrade", json={
            "suit": suit,
            "direction": direction
        })
        if r.status_code == 200:
            with command_output_field.container():
                st.write(json.loads(r.content))
            r = requests.get(url + f"/{st.session_state['user']['id']}/hand")

        else:
            print("ERROR CODE {}: {}".format(r.status_code, r.content))

    def update_polling(url):
        cache = []
        while True:
            time.sleep(0.5)
            try:
                with seconds.container():
                    r = requests.get(url + "/secondsLeft")
                    if r.status_code == 200:
                        if r.content != "Game not on":
                            x = json.loads(r.content)['time']
                            st.metric(label='Seconds', value=x)
                with orderbook.container():
                    r = requests.get(url + "/orderbookSnapshot")
                    if r.status_code == 200:
                        if r.content != "Game not on":
                            x = pd.DataFrame.from_dict(json.loads(r.content),orient = 'index')
                            x = x[['bid_user','bid','ask','ask_user']]
                            st.write(x)
                with hand.container():
                    r = requests.get(url + f"/{st.session_state['user']['id']}/hand")
                    if r.status_code == 200:
                        if r.content != "Game not on":
                            x = r.content
                            st.write(x)
                with wallet.container():
                    r = requests.get(url + f"/chipleaderboard")
                    if r.status_code == 200:
                        x = json.loads(r.content)
                        st.write(x)
                with update_board.container():
                    r = requests.get(url + f"/quoteHistory")
                    if r.status_code == 200:
                        x = pd.DataFrame(json.loads(r.content))
                        st.write(x)
            except Exception as e:
                print(e)
            r = requests.get(url + "/updates")
            with live_update_container.container():
                global results_data
                if r.status_code == 200:
                    updates = json.loads(r.content)
                    results_data = None
                    if updates == cache:
                        continue
                    else:
                        df = pd.DataFrame(updates)
                        df.time = pd.to_datetime(df.time, unit = 's')
                        st.write(df[['message','time']])
                        cache = updates
                        if df.message.isin(['Game ended']).any():
                            results_data = df[df['message'] == 'Game ended'].data.iloc[0]
            with results.container():
                st.write(results_data)



    update_polling(url)