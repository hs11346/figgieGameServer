from collections import deque
import datetime
import random
from typing import List
import copy

class Deck:

    def __init__(self,player_num : int):
        self.cards = None
        self.goal_suit = None
        self.player_num = player_num

    def shuffle(self) -> None:
        suits = [12,10,10,8]
        random.shuffle(suits)
        self.cards = {"Spades":suits[0],"Clubs":suits[1],"Diamonds":suits[2],"Hearts":suits[3]}
        self.goal_suit = None
        self.map = {
            "Spades": "Clubs",
            "Clubs": "Spades",
            "Diamonds": "Hearts",
            "Hearts": "Diamonds"
        }
        for suit in self.cards:
            if self.cards[suit] == 12:
                self.goal_suit = self.map[suit]

    def distribute(self) -> List:
        cards = copy.deepcopy(self.cards)
        card_list = []
        for key, value in cards.items():
            for _ in range(value):
                card_list.append(key)
        random.shuffle(card_list)

        sub_list_size = int(len(card_list) / self.player_num)

        players = [[] for _ in range(self.player_num)]

        # Distribute the elements of the input list into the output lists
        for i, item in enumerate(card_list):
            players[i // sub_list_size].append(item)

        players_result = []
        for item in players:
            result = {
                "Spades": 0,
                "Clubs": 0,
                "Diamonds": 0,
                "Hearts": 0
            }
            for i in item:
                result[i] += 1
            players_result.append(result)


        return players_result



class Orderbook:
    """
    Orderbook class represents the orderbook, where quotes are submitted and stored.
    """
    def __init__(self):
        self.book = {
            'Spades': {
                "bid": None,
                "ask": None,
                'bid_user' : None,
                'ask_user' : None,
            },
            'Clubs': {
                "bid": None,
                "ask": None,
                'bid_user': None,
                'ask_user': None,
            },
            'Hearts': {
                "bid": None,
                "ask": None,
                'bid_user': None,
                'ask_user': None,
            },
            'Diamonds': {
                "bid": None,
                "ask": None,
                'bid_user' : None,
                'ask_user' : None,
            }
        }

    def clear_orderbook(self) -> None:
        '''
        Clears the orderbook when a trade is filled
        :return: None
        '''
        self.book = {
            'Spades': {
                "bid": None,
                "ask": None,
                'bid_user' : None,
                'ask_user' : None,
            },
            'Clubs': {
                "bid": None,
                "ask": None,
                'bid_user': None,
                'ask_user': None,
            },
            'Hearts': {
                "bid": None,
                "ask": None,
                'bid_user': None,
                'ask_user': None,
            },
            'Diamonds': {
                "bid": None,
                "ask": None,
                'bid_user' : None,
                'ask_user' : None,
            }
        }
    def submit_quote(self, suit : str, price : int, direction : str, user : str) -> str:
        '''
        Submits a new quote to the orderbook
        :param suit: suit of the trade
        :param price: worst price that the trade can accept
        :param direction: either 'bid' or 'ask'
        :param user: username
        :return: message
        '''
        # Catching invalid parameters
        if direction not in ['bid', 'ask']:
            return 'Invalid direction'
        elif suit not in ['Hearts', 'Diamonds','Spades','Clubs']:
            return "Invalid suit"

        # Check for existing quotes in suit
        current_quote = self.book[suit][direction]
        if current_quote is None: # Enter new quote
            self.book[suit][direction] = price
            self.book[suit][direction+"_user"] = user
            return 'Order filled successfully'
        else:
            if direction == 'bid':
                if current_quote >= price: # unsuccessful
                    return 'Order failed due to not top of the book'
                if current_quote < price: # unsuccessful
                    self.book[suit][direction] = price
                    self.book[suit][direction + "_user"] = user
                    return 'Order filled successfully'
            if direction == 'ask':
                if current_quote <= price: # unsuccessful
                    return 'Order failed due to not top of the book'
                if current_quote > price: # unsuccessful
                    self.book[suit][direction] = price
                    self.book[suit][direction + "_user"] = user
                    return 'Order filled successfully'

    def submit_trade(self, suit : str, direction : str) -> list:
        """

        :param suit:
        :param direction: 'buy' or 'sell'
        :return: a list, first element is the message, second is the quote price filled (if any)
        """
        if direction not in ['buy', 'sell']:
            return ['Invalid direction',None]
        elif suit not in ['Hearts', 'Diamonds', 'Spades', 'Clubs']:
            return ["Invalid suit",None]

        book_side = None
        if direction == 'buy':
            book_side = 'ask' # the side of the book to hit
        elif direction == 'sell':
            book_side = 'bid' # the side of the book to hit

        current_quote = copy.deepcopy(self.book[suit][book_side])
        current_quote_user = copy.deepcopy(self.book[suit][book_side+"_user"])
        if current_quote is None:
            return ['No quotes to fill',None, None]
        else:
            self.clear_orderbook() # clear orderbook for new round of trading
            return ['Order matched',current_quote, current_quote_user]

class Interface:
    '''
    Interface Class represents the interface towards the matching engine.
    Users can interact with the orderbook through this class
    '''

    def __init__(self):
        self.quote_history = deque() # store all submitted quotes, successful and failed
        self.trade_history = deque() # store all successful trades
        self.start_time =  datetime.datetime.now() # record start time
        self.orderbook = Orderbook()

    def time_elasped(self):
        '''
        Returns the secnods elasped in system time
        :return: float
        '''
        return (datetime.datetime.now() - self.start_time).total_seconds()

    def access_orderbook(self):
        """
        Returns a snapshot the orderbook dictionary
        :return: dictionary
        """
        return self.orderbook.book

    def new_quote(self,  suit : str, price : int, direction : str, user : str) -> dict:
        '''
        Receives a quote and adds it to the orderbook and quote history
        :param suit:
        :param price:
        :param direction:
        :return: dictionary -> messages
        '''
        msg = self.orderbook.submit_quote(suit, price, direction, user)
        output = {"message": msg}
        if msg.startswith('Invalid'):
            return output
        if msg == 'Order filled successfully':
            self.quote_history.append((suit, price, direction, user, 'success'))
            return output
        if msg == 'Order failed due to not top of the book':
            self.quote_history.append((suit, price, direction, user, 'failed'))
            return output

    def new_trade(self, suit : str, direction : str, user : str) -> dict:
        status = self.orderbook.submit_trade(suit, direction)
        output = {'message':status[0], "price" : status[1], 'quote_from' : status[2]}
        if status[0] == 'Order matched':
            self.trade_history.append((suit, direction, status[0], status[1], user, status[2]))
            return output
        else:
            return output

