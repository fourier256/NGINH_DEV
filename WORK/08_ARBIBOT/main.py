import time
import numpy as np
import matplotlib.pyplot as plt

import multiprocessing as mp
import threading

import pybithumb
import pyupbit

import my_upbit as ub
import my_bithumb as bt
import my_telegram_bot
from my_util import print_log
from my_util import get_buf

import config

is_running = True
wm = 0
queue = 0
proc = 0

tt_now = time.time()
tt_ws_bt = tt_now
tt_ws_ub = tt_now

count = 5
amount = 1000

arbi_amount = 0

def initialize() :
    global is_running
    global wm
    global queue
    global proc

    ub.initialize()
    bt.initialize()
    bt.update_orderbook()
    ub.update_orderbook()
    my_telegram_bot.log_telegram(get_buf())
    # start websocket
    wm = pybithumb.WebSocketManager("orderbooksnapshot", ["USDT_KRW"])
    queue = mp.Queue()
    proc = mp.Process(target=pyupbit.WebSocketClient, args=('orderbook', ["KRW-USDT"], queue), daemon=True)
    proc.start()
    return 0

def main_loop() :
    while is_running :
        t0 = time.time()
        sub_loop_1s()
        t1 = time.time()
        time_elapsed = t1-t0
        if time_elapsed < 1 :
            time.sleep(1-time_elapsed)
        if time.localtime(t0).tm_min != time.localtime().tm_min :
            sub_loop_1m()
    return 0

def ws_ub_loop() :
    global tt_ws_ub
    global arbi_amount
    print('start UB WS')
    while is_running:
        tt_ws_ub = time.time()
        data = queue.get()
        ub.ask_price = int(data['orderbook_units'][0]['ask_price'])
        ub.bid_price = int(data['orderbook_units'][0]['bid_price'])
    return 0

def ws_bt_loop() :
    global tt_ws_bt
    global arbi_amount
    print('start BT WS')
    while is_running:
        tt_ws_bt = time.time()
        data = wm.get()
        bt.ask_price = int(data['content']['asks'][0][0])
        bt.bid_price = int(data['content']['bids'][0][0])
    return 0

def sub_loop_1s() :
    global is_running
    global count
    global arbi_amount

    if ub.bid_price > bt.ask_price :
        # Market Order Arbitration
        ub.update_balance()
        if ub.hold_position >= amount :
            bt.buy_market_order('USDT', amount)
            ub.sell_market_order('USDT', amount)
            print_log('Arbitration :')
            print_log(' bt.ask_price = ' + str(bt.ask_price))
            print_log(' ub.bid_price = ' + str(ub.bid_price))
            my_telegram_bot.log_telegram(get_buf())
            time.sleep(1)
            bt.widthdraw_coin('USDT', amount, config.get_config('WALLET'), 'TRX')
            arbi_amount += amount
        else :
            print_log(' ub.hold_position = 0, sleep 60sec')
            my_telegram_bot.log_telegram(get_buf())
            time.sleep(60)
    #elif ub.bid_price == bt.ask_price :
    #    # Limit Order Arbitration Try
    #    ub.update_balance()
    #    if ub.hold_position >= amount :
    #        if len(bt.orders)==0 and len(ub.orders)==0:
    #            bt.buy_limit_order('USDT', bt.bid_price, amount)
    #            ub.sell_limit_order('USDT', ub.ask_price, amount)
    #            print_log('Arbitration(Limit) :')
    #            print_log(' bt.bid_price = ' + str(bt.bid_price))
    #            print_log(' ub.ask_price = ' + str(ub.ask_price))
    #            my_telegram_bot.log_telegram(get_buf())
    #    else :
    #        print_log(' ub.hold_position = 0, sleep 60sec')
    #        my_telegram_bot.log_telegram(get_buf())
    #        time.sleep(60)
    #elif ub.bid_price < bt.ask_price :
    #    # Cancel Limit Order Arbitration (price not ok)
    #    if len(bt.orders)==1 and len(ub.orders)==1 :
    #        bt.update_orders()
    #        ub.update_orders()
    #        if bt.order_details[bt_order_id]['data']['order_status'] == 'Pending' :
    #            bt.bithumb.cancel_order(bt.orders[0])
    #            ub.upbit.cancel_order(ub.orders[0]['uuid'])
    #            print_log('Cancel Limit Order Arbitration (price not ok)')
    #
    #
    ## Limit Order Arbitration Confirm
    #if len(bt.orders)==1 and len(ub.orders)==1 :
    #    bt_order_id = bt.orders[0][2]
    #    ub_order_id = ub.orders[0]['uuid']
    #    bt.update_orders()
    #    ub.update_orders()
    #    #print(bt.orders)
    #    #print(bt.order_details)
    #    if bt.order_details[bt_order_id]['data']['order_status'] == 'Completed' :
    #        trade_price = int(bt.order_details[bt_order_id]['data']['order_price'])
    #        ub.upbit.cancel_order(ub_order_id)
    #        ub.sell_market_order('USDT', amount)
    #        print_log('Arbitration(Limit_Done) :')
    #        print_log(' bt.trade_price = ' + str(trade_price))
    #        print_log(' ub.trade_price = ' + str(ub.bid_price))
    #        my_telegram_bot.log_telegram(get_buf())
    #        time.sleep(1)
    #        bt.widthdraw_coin('USDT', amount, config.get_config('WALLET'), 'TRX')
    #    if ub.order_details[ub_order_id]['state'] == 'done' :
    #        trade_price = int(ub.order_details[ub_order_id]['price'])
    #        bt.bithumb.cancel_order(bt.orders[0])
    #        bt.buy_market_order('USDT', amount)
    #        print_log('Arbitration(Limit_Done) :')
    #        print_log(' bt.trade_price = ' + str(bt.ask_price))
    #        print_log(' ub.trade_price = ' + str(trade_price))
    #        my_telegram_bot.log_telegram(get_buf())
    #        time.sleep(1)
    #        bt.widthdraw_coin('USDT', amount, config.get_config('WALLET'), 'TRX')

    tt_now = time.time()
    if tt_now - tt_ws_bt > 60 :
        print_log('WS BT Dead')
        is_running = False
    if tt_now - tt_ws_ub > 60 :
        print_log('WS UB Dead')
        is_running = False
    return 0

def sub_loop_1m() :
    print_log('ub_bid / bt_ask : ' + str(ub.bid_price) + ' / ' + str(bt.ask_price))
    get_buf()
    return 0

def main() :
    global proc
    global wm
    initialize()
    thread_UB = threading.Thread(target=ws_ub_loop)
    thread_BT = threading.Thread(target=ws_bt_loop)
    thread_MN = threading.Thread(target=main_loop)
    thread_UB.start()
    thread_BT.start()
    thread_MN.start()
    thread_UB.join()
    thread_BT.join()
    thread_MN.join()
    wm.terminate()
    proc.kill()
    print_log('ARBIBOT Dead')
    my_telegram_bot.log_telegram(get_buf())
    exit()
    return 0

if __name__ == "__main__" :
    main()

