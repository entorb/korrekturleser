# How to deploy to Uberspace U8 / entorb.net

## FastAPI Backend

### Gunicorn

(I chose not to use venv to save space on webserver at the cost of project interdependency.)

`python3.14 -m pip install --user gunicorn`

### Backend Service

see [fastapi-korrekturleser.service](fastapi_app/fastapi-korrekturleser.service)

```sh
# update services
systemctl --user daemon-reload
# restart
systemctl --user restart fastapi-korrekturleser
# status
systemctl --user status streamlit-stats
# logs
journalctl --user -u streamlit-stats -f
# register new backend
uberspace web backend add /be/korrekturleser port 9002
# verify
uberspace web backend list
```
