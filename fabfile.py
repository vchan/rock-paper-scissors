import os
from fabric.api import *

# the user to use for the remote commands
env.user = 'vincent'
# the servers where the commands are executed
env.hosts = ['riva']

APP_NAME = 'rps'
VENV_DIR = '~/%s/env' % APP_NAME

def bootstrap():
    venv_base_dir, venv_name = os.path.dirname(VENV_DIR), os.path.basename(VENV_DIR)
    run('mkdir -p %s' % venv_base_dir)
    with cd(venv_base_dir):
        run('virtualenv --distribute %s' % venv_name)

def pack():
    ''' Create a new source distribution as tarball '''
    local('python setup.py sdist --formats=gztar', capture=False)

def deploy():
    # figure out the release name and version
    dist = local('python setup.py --fullname', capture=True).strip()
    # upload the source tarball to the temporary folder on the server
    put('dist/%s.tar.gz' % dist, '/tmp/app.tar.gz')
    # create a place where we can unzip the tarball, then enter
    # that directory and unzip it
    run('mkdir -p /tmp/app')
    with cd('/tmp/app'):
        run('tar xzf /tmp/app.tar.gz')
    with cd('/tmp/app/%s' % dist):
        # remove old static files
        run('rm -r ~/www/static')
        run('mv %s/static ~/www' % APP_NAME)
        run('mv gunicorn_config.py %s' % VENV_DIR)
        # now setup the package with our virtual environment's python
        # interpreter
        run('%s/bin/python setup.py install' % VENV_DIR)
    # now that all is set up, delete the folder again
    run('rm -rf /tmp/app /tmp/app.tar.gz')

def stop_gunicorn():
    run('kill -15 `cat /tmp/gunicorn.pid`')

def start_gunicorn():
    run('{0}/bin/gunicorn {1}:app -c {0}/gunicorn_config.py'.format(VENV_DIR, APP_NAME))

def restart_gunicorn():
    stop_gunicorn()
    start_gunicorn()
