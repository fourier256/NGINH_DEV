# Python 3
# pip3 installl pyJwt
import jwt 
import uuid
import hashlib
import time
from urllib.parse import urlencode
import requests
import json


accessKey = '3d6e7d8cac9f914e4b8d930d024f47b4'
secretKey = '87524a253f074f0a6936f07c1695a60b'
apiUrl = 'https://api.bithumb.com'

# Set API parameters
requestBody = dict( currency='USDT', net_type='TRX', amount=5, address='TJD4cbFr7raVTMe4AwgCQ6uyhcP9pYbXDZ', secondary_address=None )

# Generate access token
query = urlencode(requestBody).encode()
hash = hashlib.sha512()
hash.update(query)
query_hash = hash.hexdigest()
payload = {
    'access_key': accessKey,
    'nonce': str(uuid.uuid4()),
    'timestamp': round(time.time() * 1000), 
    'query_hash': query_hash,
    'query_hash_alg': 'SHA512',
}   
jwt_token = jwt.encode(payload, secretKey)
authorization_token = 'Bearer {}'.format(jwt_token)
headers = {
  'Authorization': authorization_token,
  'Content-Type': 'application/json'
}

try:
    # Call API
    response = requests.post(apiUrl + '/v1/withdraws/coin', data=json.dumps(requestBody), headers=headers)
    # handle to success or fail
    print(response.status_code)
    print(response.json())
except Exception as err:
    # handle exception
    print(err)