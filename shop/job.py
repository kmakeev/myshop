from fabric.api import *
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# ALLOWED_HOSTS = ['*', 'localhost']

# env.hosts = ALLOWED_HOSTS
env.project_root = BASE_DIR

def deploy_static():
    with cd(env.project_root):
        local('./manage.py collectstatic -v0 --noinput')
