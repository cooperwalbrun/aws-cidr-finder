# Contributing to aws-cidr-finder

1. [Development Workspace Setup](#development-workspace-setup)
2. [Dependency Management](#dependency-management)
   1. [Adding New Dependencies](#adding-new-dependencies)
   2. [Updating Dependencies](#updating-dependencies)
   3. [Updating Python in the Virtual Environment](#updating-python-in-the-virtual-environment)
4. [Unit Testing](#unit-testing)
5. [Running aws-cidr-finder Locally](#running-aws-cidr-finder-locally)
5. [Code Policy](#code-policy)
   1. [YAPF](#yapf)
   2. [Typing](#typing)
   3. [Imports](#imports)
7. [Changelog](#changelog)

## Development Workspace Setup

To start development and testing, ensure you have Python >=3.10 and <4.0 installed,
[activate the virtual environment](https://docs.python.org/3/tutorial/venv.html#creating-virtual-environments)
with something like

```bash
$ python -m venv venv
$ source venv/Scripts/activate
```

Then, run one of the following commands in this project's root directory:

```bash
pip install -e .[development] # Development and unit testing purposes
pip install -e .[testing]     # Unit testing purposes only
```

## Dependency Management

### Adding New Dependencies

>Before issuing these commands, **ensure that you are in the virtual environment** and that you
>executed the `pip install` command intended for development purposes (see
>[Development Workspace Setup](#development-workspace-setup)).

1. Add the package to your environment.
    ```bash
    pip install $PACKAGE # Adds the package to your virtual environment
    ```

2. Test the dependency out (i.e. write your code) to ensure it satisfies your needs and that it
   works well with existing dependencies.

3. Add a reference to the package in the appropriate place(s). You must do only **one** of the tasks
   below.
   * If it is a **unit testing-only** dependency, add it under `testing =` in `setup.cfg` and
     `deps =` in `tox.ini`.
   * If it is a **testing and development** dependency, add it under `development =` in
     `setup.cfg`.
   * If it is specific to a **GitHub Actions** workflow, add it under `github_actions =` in
     `setup.cfg`.
   * If it is a **production/runtime** dependency, add it under `install_requires =` in
     `setup.cfg`. Unless you know lower versions will work too, specify the version you installed
     as a lower bound (e.g. `somemodule>=X.Y.Z`). It is also recommended to specify an upper bound
     to avoid situations where a breaking change was introduced in a major version upgrade (e.g.
     `somemodule>=X.Y.Z,<A`)

### Updating Dependencies

>Before issuing these commands, **ensure that you are in the virtual environment**.

Simply update the version parameters in `setup.cfg` and issue the install command(s) for this
application (see [Development Workspace Setup](#development-workspace-setup) above).

### Updating Python in the Virtual Environment

After the newer version of Python is installed on your machine, then use `venv`'s built-in
functionality for upgrading Python in a virtual environment. Ensure that you execute this command
from **outside** your virtual environment, otherwise it will not work properly.

>Note: in this example, we have already updated our system path to point to the newer version of
>Python.

```bash
python -m venv --upgrade $YOUR_VENV_DIRECTORY_LOCATION
```

Alternatively, you could delete your `venv` and recreate it, though that will not be as quick as
running the command above.

## Unit Testing

To run the unit tests, **ensure you are in the virtual environment** with development or testing
dependencies installed (see above) if running tests via `setup.py`, otherwise ensure you are **not**
in a virtual environment if running tests via `tox`. Then, run the corresponding command in this
project's root directory:

```properties
python -m pytest --cov # Run unit tests using your current virtual environment's Python interpreter
tox                    # Run unit tests using tox (requires that you have the necessary Python interpreters on your machine)
```

## Running aws-cidr-finder Locally

To run the program as a CLI tool in your local development environment, you can use a command such
as the following (`--profile` argument given for demonstrative purposes):

```bash
python -m aws_cidr_finder --profile myprofile
```

## Code Policy

### YAPF

This project uses [yapf](https://github.com/google/yapf) to handle formatting, and contributions to
its code are expected to be formatted with YAPF (within reason) using the settings in
[.style.yapf](.style.yapf).

If YAPF is mangling your code in an unmaintainable fashion, you can selectively disable it using the
comments `# yapf: disable` and `# yapf: enable`. Whenever the former appears, the latter must appear
afterwards (this project will not tolerate disabling YAPF for large code blocks and/or entire
files). Disabling YAPF should be done sparingly.

### Typing

In addition to YAPF formatting, code should be appropriately accompanied by type annotations. This
includes:
* Variables and constants in global scope (regardless of whether the variable name is prefixed with
  an underscore)
* All method parameters and method return values
* Any declaration that may have a non-obvious, ambiguous, or otherwise complex type signature

In addition to type annotations, all changes to this project's code are expected to be checked with
[mypy](https://github.com/python/mypy). To run this check, simply execute the `mypy src` command at
the root of this project.

### Imports

Imports should be sorted. Most IDEs support this functionality via keybindings or even via on-save
operations.

## Changelog

This project uses a [CHANGELOG.md](CHANGELOG.md) to track changes. Please update this document along
with your changes when you make a pull request (you can place your changes beneath the `Unreleased`
section near the top). Please also tag your line items with a reference to your GitHub profile. You
should use the formatting that is already in place (see the document for more information).
