# gunicorn_config.py

bind = '127.0.0.1:8000'
workers = 2
module = 'ask_taukaeva.wsgi:application'

# accesslog = './logs/gunicorn-access.log'
# errorlog = './logs/gunicorn-error.log'
loglevel = 'debug'
daemon = False 