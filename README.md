# pypyr-scheduler 📓

[![Logo](media/logo-192.png)](https://github.com/dzerrenner/pypyr-scheduler)

Schedule [pypyr](https://github.com/pypyr/pypyr-cli) pipelines with [apscheduler](https://github.com/agronholm/apscheduler) and control them via REST. The API interface is provided by [connexion](https://connexion.readthedocs.io/en/latest/index.html).

![Travis (.org)](https://img.shields.io/travis/pypyr-scheduler/pypyr-scheduler)
![Coveralls github](https://img.shields.io/coveralls/github/pypyr-scheduler/pypyr-scheduler)
![Read the Docs](https://img.shields.io/readthedocs/pypyr-scheduler)
![GitHub](https://img.shields.io/github/license/pypyr-scheduler/pypyr-scheduler)

## Documentation status

This documentation is in a very early stage and many things could be missing or wrong. Please rely on the code for now.

## Install

Make a new venv, activate it, clone the repo, run `pip install`. No pypi release yet.
We recommend using [pipenv](https://pipenv.kennethreitz.org), which makes it easy to run commands inside a virtual env without the need to create or activate it:

    pip install --user pipenv  # only needed once per python install
    pipenv install
    pipenv run pyrsched

## Usage

*Outdated*: This section is not correct anymore.

Run `python -m pyrsched start`.
Browse to [http://localhost:8090/ui/](http://localhost:8090/ui/). New pipelines have to be present in the `pipelines` directory first before adding them. This will likely change in the future, you'll be able to upload them using the restful interface.

## Documentation

Detailed documentaion is available on [ReadThedocs](https://pypyr-scheduler.readthedocs.io). It is generated from the `docs/source` folder in this repository. Feel free to send a PR is you find any typos.

## Development

The API schema should be compliant to the [OpenAPI 3.0.0 specification](https://swagger.io/docs/specification/).

## Quick links

- <https://travis-ci.org/dzerrenner/pypyr-scheduler>
- <https://coveralls.io/github/dzerrenner/pypyr-scheduler>

## Related projects

[Flask-APScheduler](https://github.com/viniciuschiele/flask-apscheduler) provides
a similar way to run job within flask as server. It even provides a REST-API. Try this
if you don't need the functionality of pypyr.
