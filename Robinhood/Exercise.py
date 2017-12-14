import json
from Robinhood import Robinhood
my_trader = Robinhood(username="", password="")

# Getting Market Quotes from all positions owned
#docs = my_trader.get_quotes()

#Checking All orders TODO use the results for something
#orders = my_trader.check_all_orders()

#Works because positions is initialized during login
#print (json.dumps(my_trader.positions, indent=4, sort_keys=True))

#buying
#instrument = my_trader.instruments("WMIH")
#buy_res = my_trader.place_buy_order(instrument, 4)

# Sold my stock of grpn
#sell_res = my_trader.place_sell_order(my_trader.instruments(positions['GRPN']['symbol']), positions['GRPN']['quantity'])
