# w209-final-project-section7

##### Authors: Charlie Shaw, Jash Sompalli, Justin Wong, Stephen Tan

Final Project for w209 - Codebase and Collaboration

## Demo Links

- [WIP public page]
- [Dev Page](https://apps-fall22.ischool.berkeley.edu/~justinryanwong/w209/)

## Getting Started

### Development using `virutalenv` with flask

The following commands should get you started with running the flask app locally using a virtual environment that relaods with changes.

```
virtualenv venv --python=/usr/local/bin/python3.7 # Create venv virtual environment with python 3.7
source venv/bin/activate # Activate virtual environment
pip install -r requirements.txt # Install necessary packages

# Set up flask variables and run with debug mode on.
export FLASK_APP=w209.py
export FLASK_DEBUG=1
export FLASK_ENV=development
flask run
```

Alternatively, the `start_dev_app.sh` was created to run the commands for you, assuming the packages are already installed.

These instructions

## References

- [w209 web hosting via ischool servers](https://docs.google.com/document/d/1WhGPj32ukYWc-v9qEs1WmMqofmXIKm0bniJs7tG19dI/edit)
- [altair + flask](https://plainenglish.io/blog/create-a-simple-covid-19-dashboard-with-flask-plotly-altair-chart-js-and-adminlte)
