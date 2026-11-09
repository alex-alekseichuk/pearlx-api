# pearlx-api-flex
Expanding PearlX API Core capabilities to include external (3rd party user) API access - telemetry &amp; controls

This project is based of Python3 + [Flask-RESTX](https://flask-restx.readthedocs.io/en/latest/index.html) framework.

<br/>

## Machine setup
Python3.10
* Install [python3](https://www.python.org/downloads/)
    ```bash
    python3 --version
    pip3 --version
    ```

* Install [pipenv](https://pipenv.pypa.io/en/latest/)
    ```bash
    pip3 install --user --upgrade pipenv
    # put this ur ~/.zshrc or ~/.bashrc and source it (source ~/.zshrc or source ~/.bashrc)
    export PATH=~/.local/bin:$PATH
    pipenv --version
    ```

<br/>

## Soure code

## Dependency manegement
* pipenv remove any virtual environment specific to project
    ```
    pipenv --rm
    ```

* pipenv re-install any virtual environment specific to project runtime
    ```
    pipenv install
    ```

* pipenv re-install runtime + development dependencies
    ```
    pipenv install --dev
    ```

* pipenv shell
    ```bash
    pipenv shell
    python --version
    pip --version
    ```

* pipenv add a dependency to project
    ```bash
    pipenv install flask # install latest version
    pipenv install flask_restx~=0.5 # install version as per symantic versioning
    ```

* pipenv see and/or create depencencies's versions
    ```bash
    pipenv run pip freeze
    pipenv run pip freeze > requirements.txt
    ```

* pipenv create setup.py file
    ```bash
    pipenv run pip freeze
    ```


<br/>

## Configuration
### Connection to AWS Timestream
* Login into AWS app by link like:
    ```bash
    https://d-9a472fe730.awsapps.com/start
    ```

* Search IAM:
    ```bash
    Create an IAM user (first time only) or use such existing IAM user for pearlx-api-flex service talking to TimeStream database. 
    ```

* Copy credentials AWS_ACCESS_KEY_ID & AWS_SECRET_ACCESS_KEY key-vaules pairs in ur .env file or environment variables.

### Schedule synchronization with AWS Timestream
* To enable automatic synchronization in .env file specify:
    ```bash
    SCHEDULER_ENABLED=1
    ```

* Specify option when need to run synchronization using crontab syntax (for example midnight):
    ```bash
    SCHEDULER_REFRESH_SITES_CRON="0 0 * * *"
    ```


<br/>

## Running the app
* Copy .env file from given .env file template:
    ```bash
    cp .env.template .env
    ```

* For a demo, run all services and apply migrations:
    ```bash
    docker-compose up --build
    ```
  We don't need to run anything else or install python/modules.
  
* For a demo, run PostgreSQL DB only:
    ```bash
    docker-compose up postgres
    ```
  For development, we run DB in container only.
  We launch other services by hand. See below.

* Upgrade DB structure:
  ```bash
  flask db upgrade
  ```
  or in terms of pipenv:
  ```bash
  pipenv run flask db upgrade
  ```

* Start API application
    ```bash
    flask run
    ```
  or in terms of pipenv:
  ```bash
  pipenv run flask run
  ```
  
* Browse swagger at [http://localhost:5000/ui](http://localhost:5000/ui)


<br/>

## Database
* Upgrade DB structure:
    ```bash
    flask db upgrade
    ```

* Downgrade DB structure:
    ```bash
    flask db downgrade
    ```

* Create a migration by model/database difference:
    ```bash
    flask db migrate -m "Some comment"
    ```

* Create a blank migration:
    ```bash
    flask db revision -m "Some comment"
    ```
  
* Reset admin password:
  ```sql
  UPDATE public."user" SET 
    password_hash=decode('3065307443A2086097CEABFACECA5DDB462E97A15B1A9816D15825822FE77949','hex'),
    password_salt=decode('766A26608413224DFF97F1ACE3CF677122737856EEBA56A1A5C3D33DC2423975','hex')
  WHERE
    email='admin@some.com';
  ```

<br/>

## Debugging
* start [Visual Studio Code](https://code.visualstudio.com/download) debugger with option: 
* put any breakpoint in source code and see it getting hit when related API is called


<br/>

### Swagger
* Try out API at [swagger page](http://localhost:5000/).
* Browse [swagger.json](http://localhost:5000/api/v1/swagger.json).


<br/>

# Testing
## Unit
* Run unit tests by command (main options have already been set in config file):
    ```bash
    pytest
    ```

* Run unit tests with detailed coverage report in html format by command:
    ```bash
    pytest --cov-report html
    ```

* Run black code formatter:
    ```bash
    black .
    ```
* Run flake8 linter:
    ```bash
    flake8
    ```

