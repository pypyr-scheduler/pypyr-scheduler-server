# pypyr-scheduler 📓

Schedule [pypyr](https://github.com/pypyr/pypyr-cli) pipelines with [apscheduler](https://github.com/agronholm/apscheduler) and control them via REST. The API interface is provided by Zalando's [connexion](https://connexion.readthedocs.io/en/latest/index.html).

[![Test Status](https://travis-ci.org/dzerrenner/pypyr-scheduler.svg?branch=master)](https://travis-ci.org/dzerrenner/pypyr-scheduler)
[![Coverage Status](https://coveralls.io/repos/github/dzerrenner/pypyr-scheduler/badge.svg?branch=master)](https://coveralls.io/github/dzerrenner/pypyr-scheduler?branch=master)
[![Documentation Status](https://readthedocs.org/projects/pypyr-scheduler/badge/?version=latest)](https://pypyr-scheduler.readthedocs.io/en/latest/?badge=latest)

## Install

Make a new venv, activate it, clone the repo, run `pip install`. No pypi release yet.
TODO: pipenv

## Usage

Run `python -m pyrsched start`.
Browse to `http://localhost:8090/api/doc`. New pipelines have to be present in the `pipelines` directory first before adding them. This will likely change in the future, you'll be able to upload them using the restful interface.

## Documentation

Detailed documentaion is available on [ReadThedocs](https://pypyr-scheduler.readthedocs.io). It is generated from the `docs/source` folder in this repository. Feel free to send a PR is you find any typos.

## Development

The API schema should be compliant to the [OpenAPI 3.0.0 specification](https://swagger.io/docs/specification/).
