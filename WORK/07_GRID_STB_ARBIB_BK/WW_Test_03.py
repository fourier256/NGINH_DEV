#from x_coin_api_client import *
#import config

#api_key = '3d6e7d8cac9f914e4b8d930d024f47b4'
#secret_key = '87524a253f074f0a6936f07c1695a60b'
#api = XCoinAPI(api_key, secret_key)

#rgParams = {
#        'endpoint': '/trade/btc_withdrawal',
#        'units':5,
#        'address':'TJD4cbFr7raVTMe4AwgCQ6uyhcP9pYbXDZ',
#        'currency':'USDT',
#        'net_type':'TRX',
#        'exchange_name':'upbit',
#        'cust_type_cd':'01',
#        'ko_name':'강동호',
#        'en_name':'donghokang'
#        }

#rgParams = {
#        'endpoint': '/trade/btc_withdrawal',
#        'units':5,
#        'address':config.get_config('WALLET'),
#        'currency':'USDT',
#        'net_type':'TRX',
#        'exchange_name':'upbit',
#        'cust_type_cd':'01',
#        'ko_name':config.get_config('KO_NAME'),
#        'en_name':config.get_config('EN_NAME')
#        }
#result = api.xcoinApiCall(rgParams['endpoint'], rgParams)

#print(result)

import my_bithumb as bt
import config

bt.initialize()
bt.widthdraw_coin('USDT', 5, config.get_config('WALLET'), 'TRX')
