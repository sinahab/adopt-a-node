
# Adopt a Node

## Setup

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

## In production
To deploy app:
```
workon adopt-a-node
pip install -r requirements.txt

export FLASK_APP=run.py
flask db upgrade

# make sure correct production secrets exist in instance/config.py

service adopt-celery restart
service adopt-web restart
```

## In development
```
ngrok http 5000  # Make localhost publicly available for Bitpay callback requests
# update APP_BASE_PUBLIC_URI in config.py

workon adopt-a-node
export FLASK_APP=run.py
flask run

celery -A app.tasks worker --loglevel=info
```

## Misc.
View scheduled Celery tasks:
```
celery -A app.tasks inspect scheduled
```

View Celery logs:
```
sudo journalctl -u adopt-celery
```

To run shell:
```
flask shell
```

To run tests:
```
FLASK_CONFIG=test python tests.py
```

Database migrations:
```
flask db migrate -m create_users
flask db upgrade
```

Assets:
```
flask assets  # to see available commands
flask assets build  # to build assets
flask assets clean  # to clean assets
```

When done iterating on UI, clean assets, and build them once:
```
flask assets clean
flask assets build
```

Add installed packages to requirements.txt
```
pip freeze > requirements.txt
```
