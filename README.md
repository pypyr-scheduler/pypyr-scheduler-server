
[![Logo](media/logo-192.png)](https://github.com/dzerrenner/pypyr-scheduler)

Schedule [pypyr](https://github.com/pypyr/pypyr-cli) pipelines with [apscheduler](https://github.com/agronholm/apscheduler) and control them via REST. The API interface is provided by [connexion](https://connexion.readthedocs.io/en/latest/index.html).

![Travis (.org)](https://img.shields.io/travis/pypyr-scheduler/pypyr-scheduler-server)
![Coveralls github](https://img.shields.io/coveralls/github/pypyr-scheduler/pypyr-scheduler-server)
[![Documentation Status](https://readthedocs.org/projects/pypyr-scheduler/badge/?version=latest)](https://pypyr-scheduler.readthedocs.io/en/latest/?badge=latest)
![GitHub](https://img.shields.io/github/license/pypyr-scheduler/pypyr-scheduler-server)

## Documentation status

This documentation is in a very early stage and many things could be missing or wrong. Please rely on the code for now.

## Install

Make a new venv, activate it, clone the repo, run `pip install`. No pypi release yet.
We recommend using [pipenv](https://pipenv.kennethreitz.org), which makes it easy to run commands inside a virtual env without the need to create or activate it:

    pip install --user pipenv  # only needed once per python install
    pipenv install
    pipenv run server

## Usage

`pypyr-scheduler` needs a shared secret between the server and the client.
It reads it from the environment variable `PYRSCHED_SECRET`.
If the server does not see a secret it generates it and writes it to its
logfile for later use. If there is a secret set in the environment, it is used.

A client needs the same shared secret.

### Development / Testing 

Run `pipenv run server`. Now you can connect to the server with a suitable client. 
Currently available are `pypyr-scheduler-cli` and `pypyr-scheduler-rpc-client` with the first one depending on the latter.

### Production deployment

TBD.

## Documentation

Detailed documentaion is available on [ReadTheDocs](https://pypyr-scheduler.readthedocs.io).
It is generated from the `docs/source` folder in this repository. Feel free to send a PR is you find any typos.

## Development

Run tests with `pipen run tests`.

## Quick links

- <https://travis-ci.org/pypyr-scheduler/pypyr-scheduler>
- <https://coveralls.io/github/pypyr-scheduler/pypyr-scheduler>

## Related projects

[pypyr](https://github.com/pypyr/pypyr-cli) is the workhorse underlying pypyr-scheduler.
It runs pipelines defines as .yaml file and has many different pipeline steps included.
Check it out, if you need a simple task automation for one-shot execution.

[Flask-APScheduler](https://github.com/viniciuschiele/flask-apscheduler) provides
a similar way to run job within flask as server. It even provides a REST-API. Try this
if you don't need the functionality of pypyr.

