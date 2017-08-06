
## To setup the app

Install virtualenv
```
pip install virtualenv  # or (conda install virtualenv) if using Anaconda Python
pip install virtualenvwrapper
export WORKON_HOME=~/Envs
source /usr/local/bin/virtualenvwrapper.sh
```

Create and activate the virtualenv
```
mkvirtualenv adopt-a-node
workon adopt-a-node
pip install -r requirements.txt
```

Install Stylus (the Javascript css preprocessor):
```
npm install -g stylus
```

Make sure the correct secrets exist in instance/development.py
```
cp instance/env.py.example instance/development.py
# update values in development.py to real values
```

Setup the database:
```
psql -c 'CREATE DATABASE adoptanode_development'
flask db upgrade
```

Bitcoin payments:
The [Bitpay Ruby docs](https://github.com/bitpay/ruby-client/blob/master/GUIDE.md#bitpay-authentication) are the best I've seen on how to set up authentication for the Bitpay API. In a Python REPL, do the following:
```
from bitpay.client import Client
client = Client()
pairing_code = client.create_token('merchant')
# 1. Paste this pairing_code into the Merchant UI to activate it and get a key.
# 2. Save client.pem into instance/bitpay-key.pem
# 3. Save client.token into the BITPAY_TOKEN config variable in instance/config.py
```

For Testnet API connection, initialize the Client as follows:
```
client = Client(api_uri="https://test.bitpay.com")
```
and use the test.bitpay.com Merchant UI.
