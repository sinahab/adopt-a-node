
## To develop locally

Do the following:

```
ngrok http 5000  # Make localhost publicly available for Bitpay callback requests
# update APP_BASE_PUBLIC_URI in config.py

workon adopt-a-node
export FLASK_APP=run.py
flask run

celery -A app.tasks worker --loglevel=info
```
