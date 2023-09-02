# Contributing

Contributions are welcome and highly appreciated!

## Feature suggestions and bug reports

If you have any feature suggestions or encounter any bugs, please create an [issue](https://github.com/realshouzy/YTDownloader/issues) in the project's repository. The case will be reviewed and if it is legitimate, you are welcome to work on addressing the issue and creating a [pull request](https://github.com/realshouzy/YTDownloader/pulls).

## TODO

Check out the [TODO](/TODO.md) file for a list of pending tasks and future improvements.

## Getting started

To start working on this project, first, clone the repository:

```bash
git clone https://github.com/realshouzy/YTDownloader.git && cd YTDownloader
```

### Setting up a virtual environment

It is highly recommended to utilize a virtual environment to develop on this project. The easiest way to set up a virtual environment is by using tox:

```bash
tox --devenv venv
```

Otherwise you could also use [``virtualenv``](https://virtualenv.pypa.io/en/latest) or [``venv``](https://docs.python.org/3/library/venv.html).

#### Install development dependencies (only necessary for ``virtualenv`` or ``venv``)

To install all the tools, plugins and other dependencies used for development, run this:

```bash
pip install -r requirements-dev.txt
```

#### Setting up the ``pre-commit`` hooks

With the environment activated run:

```bash
pre-commit install
```

### Running tests and code linting

This project utilizes [``tox``](https://tox.wiki/en/latest), so to run everything (tests and pre-commit), run this:

```bash
tox r
```

#### Running only tests

Running only the tests can be done by running:

```bash
tox r -e py311 # or the interpreter version of choice
```

Alternatively, the tests can be directly run using:

```bash
pytest
```

To only run a specific test run:

```bash
pytest -k test_name_of_the_test
```

#### Code linting

The linting and formatting is done using ``pre-commit``, thus run:

```bash
pre-commit run --all-files
```

</br>

If any questions should arise, feel free to create an [issue](https://github.com/realshouzy/YTDownloader/issues) and ask for assistance.

**Thank you for understanding and your willingness to contribute to this project!**
