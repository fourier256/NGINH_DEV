
import multiprocessing as mp
import threading
import time

import pybithumb
import pyupbit

wm = 0
queue = 0
proc = 0

def initialize() :
    global wm
    global queue
    global proc
    wm = pybithumb.WebSocketManager("orderbooksnapshot", ["USDT_KRW"])
    queue = mp.Queue()
    proc = mp.Process(target=pyupbit.WebSocketClient, args=('orderbook', ["KRW-USDT"], queue), daemon=True)
    proc.start()
    return 0

def main_loop() :
    while True:
        print('main_loop_1s')
        time.sleep(1)
    return 0

def ws_bt_loop() :
    print('start A')
    while True:
        data = wm.get()
        ask_price = data['content']['asks'][0][0]
        bid_price = data['content']['bids'][0][0]
        print('BT: ' + str(ask_price) + ' / ' + str(bid_price))
    return 0

def ws_ub_loop() :
    print('start B')
    while True:
        data = queue.get()
        ask_price = data['orderbook_units'][0]['ask_price']
        bid_price = data['orderbook_units'][0]['bid_price']
        print('UB: ' + str(ask_price) + ' / ' + str(bid_price))
    return 0

def main() :
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

if __name__ == "__main__":
    main()
