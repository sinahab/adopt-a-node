
from fabric.api import cd, run, shell_env, prefix

def deploy():
    with cd('/home/bu/adopt-a-node'):

        run('git pull')

        with shell_env(FLASK_APP='run.py'):
            with prefix('workon adopt-a-node'):
                run('pip install -r requirements.txt')
                run('FLASK_CONFIG=production flask db upgrade')

                run('sudo service adopt-web restart')
                run('sudo service adopt-celery restart')
                run('sudo service adopt-celery-beat restart')
