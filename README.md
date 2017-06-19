
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

## To run shell
```
export FLASK_APP=run.py
flask shell
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
