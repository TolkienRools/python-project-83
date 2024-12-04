# Page analyzer ([render.com link](https://python-project-83-ge25.onrender.com))

<hr>

### Hexlet tests and linter status:
[![Actions Status](https://github.com/TolkienRools/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/TolkienRools/python-project-83/actions)
[![Actions Status](https://github.com/TolkienRools/python-project-83/actions/workflows/page-analyzer-check.yml/badge.svg)](https://github.com/TolkienRools/python-project-83/actions)
[![Maintainability](https://api.codeclimate.com/v1/badges/c6853a61be89c3dfd3bf/maintainability)](https://codeclimate.com/github/TolkienRools/python-project-83/maintainability)

<hr>

## Description

Provides basic info provided by site to search engine.

### Allow:
- Add sites for check
- Get basic info via check
- Show list of checked or prepared for check sites

## Requirements

- Python >= 3.10
- poetry >= 1.8.2

## Installing

Firstly you should install latest version of poetry package.

With pip:

```shell
pip install poetry
```

With pipx:

```shell
pipx install poetry
```

Export required ENV variables
(url template: postgresql://username[:password]@host[:port]/db_name)

```shell
export SECRET_KEY = ...
export DATABASE_URL = ... 
```


Then you should install project dependencies and add tables to DB:

```shell
make build
```


## Running app

To start app in dev mode:

```shell
make dev
```

To start app for production:

```shell
make start
```
