# How to deploy to Uberspace / entorb.net

## FastAPI Backend

### Gunicorn

(I chose not to use venv to save space on webserver at the cost of project interdependency.)

```sh
pip3.13 install --user gunicorn uvloop httptools

less ~/etc/services.d/korrekturleser-fastapi.ini

[program:korrekturleser-fastapi]
directory=%(ENV_HOME)s/be/korrekturleser
command=/home/entorb/.local/bin/gunicorn --config %(ENV_HOME)s/be/korrekturleser/fastapi_app/gunicorn_conf.py
loglevel=info
# `startsecs` is set by Uberspace monitoring team, to prevent a broken service from looping
startsecs=30
```

### Register backend

```sh
uberspace web backend list
uberspace web backend set be/korrekturleser --http --port 9002
```
