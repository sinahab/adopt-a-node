
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

Install Stylus (the Javascript css preprocessor):
```
    npm install -g stylus
```
