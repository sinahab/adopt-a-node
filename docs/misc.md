
## Misc. Commands

View scheduled Celery tasks:
```
celery -A app.tasks inspect scheduled
```

View Celery logs:
```
sudo journalctl -u adopt-celery
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

Add installed packages to requirements.txt
```
pip freeze > requirements.txt
```

To run shell:
```
flask shell
```
