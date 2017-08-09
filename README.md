
# Adopt a Node

To setup the app: view [setup.md](./docs/setup.md)

To work on app locally: view [dev.md](./docs/dev.md)

To update nodes to a new version of BU: view [update.md](./docs/update.md)

To run tests:
```
FLASK_CONFIG=test python tests.py
```

To deploy app:
```
# Push changes to Github. Then:
fab -H bu@<production-ip> deploy
```

Other misc commands (database migrations, celery logs, etc.): view [misc.md](./docs/misc.md)
