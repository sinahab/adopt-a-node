
# Adopt a Node

## Setup

Install virtualenv
```
pip install virtualenv   # or (conda install virtualenv) if using Anaconda Python
pip install virtualenvwrapper
export WORKON_HOME=~/Envs
source /usr/local/bin/virtualenvwrapper.sh
```

Create and activate the virtualenv
```
mkvirtualenv adopt-a-node
workon adopt-a-node
```

Remember to add installed packages to requirements.txt
```
pip freeze > requirements.txt
```

Install Stylus (the Javascript css preprocessor):
```
npm install -g stylus
```

## To run app
```
export FLASK_APP=run.py
flask run
```

OR

```
gunicorn --bind 0.0.0.0:5000 wsgi:app
```

## To run Celery server
```
celery -A app.tasks worker --loglevel=info &
```

To view scheduled tasks:
```
celery -A app.tasks inspect scheduled
```

## To run shell
```
export FLASK_APP=run.py
flask shell
```

## To run tests
```
python tests.py
```

## Database migrations
To create a migration:
```
flask db migrate -m create_users
```

To run the migration:
```
flask db upgrade
```

## Assets
This app uses flask-assets to manage assets.

To see available commands:
```
flask assets
```

To build assets:
```
flask assets build
```

To clean assets:
```
flask assets clean
```

When done iterating on UI, clean assets, and build them once:
```
flask assets clean
flask assets build
```

## Bitcoin payments
The [Ruby docs](https://github.com/bitpay/ruby-client/blob/master/GUIDE.md#bitpay-authentication) are the best I've seen on how to set up authentication for the Bitpay API. In a Python REPL, do the following:
```
from bitpay.client import Client
client = Client()
pairing_code = client.create_token('merchant')
# 1. Paste this pairing_code into the Merchant UI to activate it and get a key.
# 2. Save client.pem into instance/bitpay-key.pem
# 3. Save client.token into the BITPAY_TOKEN config variable in instance/config.py
```

If you would like to set up a Testnet API connection, modify the line where Client is initialize to the following:
```
client = Client(api_uri="https://test.bitpay.com")
```
And use the test.bitpay.com Merchant UI.

## To run production server
```
export FLASK_APP=run.py
flask db upgrade
celery -A app.tasks worker --loglevel=info &
service adopt-a-node restart
```
