# pypyr-scheduler 📓
Schedule [pypyr](https://github.com/pypyr/pypyr-cli) pipelines with [apscheduler](https://github.com/agronholm/apscheduler) and control them via REST. The API interface is provided by Zalando's [connexion](https://connexion.readthedocs.io/en/latest/index.html).

## Install
Make a new venv, activate it, clone the repo, run `pip install`. No pypi release yet.
TODO: pipenv

## Usage
Run `python -m pyrsched start`.
Browse to `http://localhost:8090/api/doc`. New pipelines have to be present in the `pipelines` directory first before adding them. This will likely change in the future, you'll be able to upload them using the restful interface.

## Development
The API schema was created with [Spotlight Studio](https://stoplight.io/studio/). It should be compliant to the [OpenAPI 3.0.0 specification](https://swagger.io/docs/specification/).
