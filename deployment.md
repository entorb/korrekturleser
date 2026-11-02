# How to deploy to Uberspace U8 / entorb.net

## FastAPI Backend

### Uvicorn

(I chose not to use venv to save space on webserver at the cost of project interdependency.)

Plain uvicorn, no gunicorn (single user, saves RAM). Installed via `requirements.txt` by `scripts/deploy.sh`.
Logs go to journald (no more `error.log`/`access.log`).

### Backend Service

see [fastapi-korrekturleser.service](fastapi_app/fastapi-korrekturleser.service)

```sh
# update services (after changing the .service file)
cp ~/be/korrekturleser/fastapi_app/fastapi-korrekturleser.service ~/.config/systemd/user/
systemctl --user daemon-reload
# restart
systemctl --user restart fastapi-korrekturleser
# status
systemctl --user status fastapi-korrekturleser
# logs
journalctl --user -u fastapi-korrekturleser -f
# register new backend
uberspace web backend add /be/korrekturleser port 9002
# verify
uberspace web backend list
```
