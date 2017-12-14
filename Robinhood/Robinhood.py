import requests
import urllib
from collections import defaultdict

class Robinhood:

    endpoints = {
            "login": "https://api.robinhood.com/api-token-auth/",
            "investment_profile": "https://api.robinhood.com/user/investment_profile/",
            "accounts":"https://api.robinhood.com/accounts/",
            "ach_iav_auth":"https://api.robinhood.com/ach/iav/auth/",
            "ach_relationships":"https://api.robinhood.com/ach/relationships/",
            "ach_transfers":"https://api.robinhood.com/ach/transfers/",
            "applications":"https://api.robinhood.com/applications/",
            "dividends":"https://api.robinhood.com/dividends/",
            "edocuments":"https://api.robinhood.com/documents/",
            "instruments":"https://api.robinhood.com/instruments/",
            "margin_upgrades":"https://api.robinhood.com/margin/upgrades/",
            "markets":"https://api.robinhood.com/markets/",
            "notifications":"https://api.robinhood.com/notifications/",
            "positions":"https://api.robinhood.com/positions/",
            "orders":"https://api.robinhood.com/orders/",
            "password_reset":"https://api.robinhood.com/password_reset/request/",
            "quotes":"https://api.robinhood.com/quotes/",
            "document_requests":"https://api.robinhood.com/upload/document_requests/",
            "user":"https://api.robinhood.com/user/",
            "watchlists":"https://api.robinhood.com/watchlists/",
            "margin_interest_charges": "https://api.robinhood.com/cash_journal/margin_interest_charges/",
            "subscription_fees": "https://api.robinhood.com/subscription/subscription_fees/",
            "id_documents": "https://api.robinhood.com/upload/photo_ids/",
            "portfolios": "https://api.robinhood.com/portfolios/",
            "wire_relationships": "https://api.robinhood.com/wire/relationships/",
            "ach_queued_deposit": "https://api.robinhood.com/ach/queued_deposit/",
            "subscriptions": "https://api.robinhood.com/subscription/subscriptions/",
            "wire_transfers": "https://api.robinhood.com/wire/transfers/",
            "notification_settings": "https://api.robinhood.com/settings/notifications/",
            "ach_deposit_schedules": "https://api.robinhood.com/ach/deposit_schedules/",
            "password_change": "https://api.robinhood.com/password_change/"
    }

    session = None

    username = None

    password = None

    headers = None

    auth_token = None

    account_url = None

    positions = {}

    def __init__(self, username, password):
        self.session = requests.session()
        self.session.proxies = urllib.request.getproxies()
        self.username = username
        self.password = password
        self.headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en;q=1, fr;q=0.9, de;q=0.8, ja;q=0.7, nl;q=0.6, it;q=0.5",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "X-Robinhood-API-Version": "1.0.0",
            "Connection": "keep-alive",
            "User-Agent": "Robinhood/823 (iPhone; iOS 7.1.2; Scale/2.00)"
        }
        
        self.session.headers = self.headers
        self.login()
        self.get_all_positions()
        
        ## set account url
        acc = self.get_account_number()
        self.account_url = self.endpoints['accounts'] + acc + "/"

        ## printing different things
        print(self.account_url) ## account url
        sum = 0
        for k, v in self.positions.items():
            print ("%s: %i" % (k, v['quantity']))
            sum += v['quantity']

        print("Total Stocks: %i" % sum)
 
    def login(self):
        data = "password=%s&username=%s" % (self.password, self.username)
        res = self.session.post(self.endpoints['login'], data=data)
        res = res.json()
        self.auth_token = res['token']
        self.headers['Authorization'] = 'Token '+self.auth_token


    def get_all_positions(self):
        res = self.session.get(self.endpoints['positions'])
        res = res.json()['results']
        len_of_res = len(res)
        for dict in res:
            instrument = dict['instrument']
            symbol = self.session.get(instrument).json()['symbol']
            quantity = int(float(dict['quantity']))
            if quantity > 0:
                self.positions.update({symbol: {'symbol':symbol, 'quantity':quantity}})

    def get_quotes(self):
        quoteData = {}
        for key in self.positions:
            params = { 'symbols': key }
            res = self.session.get(self.endpoints['quotes'], params=params)
            res = res.json()['results'][0]
            quote = {
                'ask_price': res['ask_price'],
                'ask_size': res['ask_size'],
                'bid_price': res['bid_price'],
                'bid_size': res['bid_size'],
                'last_trade_price': res['last_trade_price'],
                'last_trade_price_source': res['last_trade_price_source']
            }
            quoteData.update({res['symbol']: quote})
        return quoteData


    def get_account_number(self):
        res = self.session.get(self.endpoints['accounts'])
        res =  res.json()['results']
        account_number = res[0]['account_number']
        return account_number

    def investment_profile(self):
        self.session.get(self.endpoints['investment_profile'])

    def get_position(self, stock):
        instrument = self.instruments(stock)[0]
        instrument_id = instrument['id']
        name = instrument['name']
        symbol = instrument['symbol']
        url = "%spositions/%s" % (self.account_url,instrument_id)
        res = self.session.get(url)
        res = res.json()
        if 'quantity' in res:
            print("You own "+res['quantity']+" shares of: "+name)
            return res['quantity']
        else:
            print("You have own none of: "+name)
            return 0
        

    def instruments(self, stock=None):
        res = self.session.get(self.endpoints['instruments'], params={'query':stock.upper()})
        res = res.json()
        return res['results'][0]

    def quote_data(self, stock):
        params = { 'symbols': stock }
        res = self.session.get(self.endpoints['quotes'], params=params)
        res = res.json()
        return res['results']

    def place_order(self, instrument, quantity=1, bid_price = None, transaction=None):
        if bid_price == None:
            bid_price = self.quote_data(instrument['symbol'])[0]['bid_price']
        data = 'account=%s&instrument=%s&price=%f&quantity=%d&side=%s&symbol=%s&time_in_force=gfd&trigger=immediate&type=market' % (urllib.parse.quote(self.account_url), urllib.parse.unquote(instrument['url']), float(bid_price), quantity, transaction, instrument['symbol']) 
        res = self.session.post(self.endpoints['orders'], data=data)
        return res.json()

    def place_buy_order(self, instrument, quantity, bid_price=None):
        transaction = "buy"
        return self.place_order(instrument, quantity, bid_price, transaction)

    def place_sell_order(self, instrument, quantity, bid_price=None):
        transaction = "sell"
        return self.place_order(instrument, quantity, bid_price, transaction)

    def check_all_orders(self):
        res = self.session.get(self.endpoints['orders'])
        res = res.json()
        return res
