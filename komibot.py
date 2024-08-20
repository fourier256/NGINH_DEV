import time

import my_telegram_bot
import my_korbit as kb

def initialize() :
kb.initialize()
return 0

def main_loop() :
while True:
tt = time.time()

kb.update_balance()
kb.update_orderbook()
try :
kb.update_order()
except :
my_telegram_bot.log_telegram('update_order failed')
print(str(kb.ask_order))
print(str(kb.bid_order))


if kb.ask_order['data']['status']=='filled' or kb.ask_order['data']['status']=='canceled' :
if kb.hold_position > 100 :
try :
kb.sell_limit_order('USDT', kb.ask_price[0], min(kb.hold_position, 5000))
my_telegram_bot.log_telegram('sell_limit_order at ' + str(kb.ask_price[0]) + ' , ' + str(min(kb.hold_position, 5000)))
except :
my_telegram_bot.log_telegram('sell order failed')
else :
if round(float(kb.ask_order['data']['price'])) > kb.ask_price[0]:
try:
kb.cancel_order(kb.ask_order['data']['orderId'])
except :
my_telegram_bot.log_telegram('cancel ask order failed')
print(str(kb.ask_order))
print(str(kb.bid_order))
if kb.bid_order['data']['status']=='filled' or kb.bid_order['data']['status']=='canceled' :
if kb.hold_position < 19000 :
kb.buy_limit_order('USDT', kb.bid_price[0], min(19000-kb.hold_position, 5000))
my_telegram_bot.log_telegram('buy_limit_order at ' + str(kb.bid_price[0]) + ' , ' + str(min(19000-kb.hold_position, 5000)))
else :
if round(float(kb.bid_order['data']['price'])) < kb.bid_price[0]:
kb.cancel_order(kb.bid_order['data']['orderId'])

time_elapsed = time.time()-tt
if(time_elapsed < 0.5) :
time.sleep(0.5-time_elapsed)
return 0

def main() :
initialize()
main_loop()
return 0

if __name__ == "__main__":
main()
