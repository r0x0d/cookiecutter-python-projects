#!/usr/bin/env python
import os
import subprocess

PROJECT_DIRECTORY = os.path.realpath(os.path.curdir)


def remove_file(filepath):
    os.remove(os.path.join(PROJECT_DIRECTORY, filepath))


if __name__ == "__main__":
    if "Not open source" == "{{ cookiecutter.open_source_license }}":
        remove_file("LICENSE")

    subprocess.check_call(["git", "init"])
    subprocess.check_call(
        [
            "git",
            "remote",
            "add",
            "origin",
            "git@github.com:{{ cookiecutter.github_username }}/{{ cookiecutter.project_name }}",  # noqa: E501
        ],
    )
