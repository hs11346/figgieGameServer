from flask import Flask, request
from objects import *
import threading

app = Flask(__name__)

game_on = False
update_log = deque(maxlen=100)
time_limit = 3*60 # in seconds
players = {} # player username : player_id
inverse = {} # player id : username
hands = {} # player_id : hand (dictionary)
wallets = {} # player_id : chip count
update_log.append({
            "time": datetime.datetime.now().timestamp(),
            'message': f'The Server has started!',
            'data': None
        })

def end_game_calculations():
    '''
    Ends the game and distributes the ante, announces winner and goal suit
    '''
    global ante
    max_player_count = 0
    max_player = None
    for player_id in players.values():
        wallets[player_id] += hands[player_id][goal_suit] * 10
        ante -= hands[player_id][goal_suit] * 10
        if hands[player_id][goal_suit] > max_player_count:
            max_player = player_id
            max_player_count = hands[player_id][goal_suit]
    wallets[max_player] += ante
    update_log.clear()
    msg = {
        "time" : datetime.datetime.now().timestamp(),
        "message" : "Game ended",
        "data" : {
            "goal suit": goal_suit,
            "wallets": str({ inverse[key]:value for (key, value) in wallets.items()})
        }

    }

    update_log.append(msg)




def timer(time_limit):
    '''
    Thread function for calculating timer and end game
    '''
    global game_on
    while True:
        seconds = interface.time_elasped()
        if seconds >= time_limit:
            game_on = False
            end_game_calculations()
            break

@app.route("/updates")
def updates():
    """
    Implements an iterative polling mechnanism for updating players, retrieves updates from broadcast
    :return: updqte_log
    """
    return list(update_log)

@app.route("/<playerid>/accessWallet")
def wallet(playerid):
    playerid = int(playerid)
    return {"data":wallets[playerid]}

@app.route("/chipleaderboard")
def leaderboard():
    public_wallet = {}
    for id in wallets:
        public_wallet[inverse[id]] = wallets[id]
    return public_wallet

@app.route("/secondsLeft")
def get_seconds_left():
    if game_on:
        return {"time":interface.time_elasped()}
    else:
        return {"time":0}

@app.route("/join", methods = ["POST"])
def join():
    '''
    Player join request
    :return: unique player_id which is used to access player's private functions
    '''
    user = request.json['username']
    if user in players:
        return {"message":"username not unique, please retry","id":None}
    else:
        players[user] = int(datetime.datetime.now().timestamp() * random.randint(2,256))
        inverse[players[user]] = user
        wallets[players[user]] = 300
        update_log.append({
            "time": datetime.datetime.now().timestamp(),
            'message': f'Player {user} has joined the game!',
            'data': None
        })
        return {"message":"success","id":players[user]}

@app.route("/<player_id>/hand")
def retrieve_hand(player_id):
    player_id = int(player_id)
    if game_on:
        if player_id not in players.values():
            return "Invalid player_id"
        else:
            return hands[player_id]
    else:
        return "Game not on"


@app.route('/start', methods = ['POST'])
def start():  # put application's code here
    global ante
    global game_on
    status = request.json['status']
    playernum = len(players)
    ante = 50*playernum

    if status == 'start' and game_on == False:
        global interface
        global deck
        global hands
        global goal_suit
        interface = Interface()
        deck = Deck(playernum)
        deck.shuffle()
        tmp = deck.distribute() # list of dict
        player_ids = list(players.values())
        for i in range(len(tmp)):
            hands[player_ids[i]] = tmp[i]
            wallets[player_ids[i]] -= 50
        update_log.append({
            "time" : datetime.datetime.now().timestamp(),
            'message': 'started',
            'data' : None
        })
        goal_suit = deck.goal_suit
        game_on = True
        timer_thread = threading.Thread(target=timer, args=(time_limit,))
        timer_thread.start()
        return 'Round started'
    else:
        return "Invalid status"

@app.route('/orderbookSnapshot')
def snapshot():  # put application's code here
    if game_on:
        return interface.access_orderbook()
    else:
        return "Game not on"

@app.route('/tradeHistory')
def tradeHistory():  # put application's code here
    if game_on:
        return list(interface.trade_history)
    else:
        return "Game not on"

@app.route('/quoteHistory')
def quoteHistory():  # put application's code here
    if game_on:
        return list(interface.quote_history)
    else:
        return "Game not on"

@app.route('/<player_id>/submitQuote', methods = ['POST'])
def quote(player_id) -> dict:  # put application's code here
    if game_on:
        player_id = int(player_id)
        if player_id not in players.values():
            return {"message":"Invalid player_id"}
        else:
            suit = request.json['suit']
            price = request.json['price']
            direction = request.json['direction']
            user = inverse[player_id]

            # check if player has enough cards or chips to execute quote
            if hands[player_id][suit] == 0 and direction == 'ask':
                msg = {"message":"No cards to sell"}
            elif wallets[player_id] < price and direction == 'bid':
                msg = {"message":'Not enough money to buy'}
            else:
                msg = interface.new_quote(suit,price,direction,user)
                request.json['status'] = msg['message']
                update_log.append({
                    "time": datetime.datetime.now().timestamp(),
                    'message': 'New quote sent',
                    'data': request.json
                })

            return msg
    else:
        return {"message":"Game not on"}

@app.route('/<player_id>/submitTrade', methods = ['POST'])
def trade(player_id):  # put application's code here
    if game_on:
        player_id = int(player_id)
        if player_id not in players.values():
            return "Invalid player_id"
        else:
            suit = request.json['suit']
            direction = request.json['direction']
            user = inverse[player_id]
            msg = interface.new_trade(suit,direction, user)
            request.json['status'] = msg['message']
            if msg['message'] == 'Order matched':
                # Trade matched, handle transaction -> chips & card exchange
                price_traded = msg['price']
                quote_from = msg['quote_from']

                # Debit and credit
                if direction == 'buy':
                    wallets[player_id] -= price_traded
                    wallets[players[quote_from]] += price_traded
                    hands[player_id][suit] += 1
                    hands[players[quote_from]][suit] -= 1
                if direction == 'sell':
                    wallets[player_id] += price_traded
                    wallets[players[quote_from]] -= price_traded
                    hands[player_id][suit] -= 1
                    hands[players[quote_from]][suit] += 1

            update_log.append({
                "time": datetime.datetime.now().timestamp(),
                'message': 'New trade sent',
                'data': request.json
            })
            return msg
    else:
        return {"message":"Game not on"}


if __name__ == '__main__':
    app.run()
