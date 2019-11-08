# pypyr-scheduler 📓
Schedule [pypyr](https://github.com/pypyr/pypyr-cli) pipelines with [apscheduler](https://github.com/agronholm/apscheduler) and control them via REST ([aiohttp-swagger](https://github.com/cr0hn/aiohttp-swagger)).

## Install
Make a new venv, activate it, clone the repo, run `pip install`

## Usage
Run `python -m pyrsched start`.
Browse to `http://localhost:8090/api/doc`. New pipelines have to be present in the `pipelines` directory first before adding them. This will likely change in the future, you'll be able to upload them using the restful interface.
