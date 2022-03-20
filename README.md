[![Tests](https://github.com/abadger/cookiecutter-python-projects/actions/workflows/tests.yml/badge.svg)](https://github.com/abadger/cookiecutter-python-projects/actions/workflows/tests.yml)

# Cookiecutter Python Projects

My personal cookiecutter repository template packed with everything I need when creating a new project.

## How to use this template

It's pretty simple and straight-forward to use this template, first you need to install `cookiecutter` and `git` in your machine.

```bash
python3 -m pip install cruft

# If you are in any debian-like distros, run:
apt install git

# If you are in fedora-like distros, run:
dnf install git
```

Then, after those dependencies are installed, simply run the following command:

```bash
# If you are using git with SSH
cruft create git@github.com:r0x0d/cookiecutter-python-projects

# If you are using git with HTTPS
cruft create https://github.com/r0x0d/cookiecutter-python-projects
```

That's it! Answer the questions that will show in your terminal and you're done!
