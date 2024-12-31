import my_bithumb as bt

bt.initialize()
result = bt.withdraw_coin('USDT', 'TJD4cbFr7raVTMe4AwgCQ6uyhcP9pYbXDZ', 5, 'TRX', None)
print(result)
