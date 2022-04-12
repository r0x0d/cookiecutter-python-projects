import datetime
import os
import shlex
import subprocess
import sys
from contextlib import contextmanager

import pytest
from cookiecutter.utils import rmtree


@contextmanager
def inside_dir(dirpath):
    """
    Execute code from inside the given directory
    :param dirpath: String, path of the directory the command is being run.
    """
    old_path = os.getcwd()
    try:
        os.chdir(dirpath)
        yield
    finally:
        os.chdir(old_path)


@contextmanager
def bake_in_temp_dir(cookies, *args, **kwargs):
    """
    Delete the temporal directory that is created when executing the tests
    :param cookies: pytest_cookies.Cookies,
        cookie to be baked and its temporal files will be removed
    """
    result = cookies.bake(*args, **kwargs)
    print(result)
    try:
        yield result
    finally:
        rmtree(str(result.project_path))


def run_inside_dir(command, dirpath):
    """
    Run a command from inside a given directory, returning the exit status
    :param command: Command that will be executed
    :param dirpath: String, path of the directory the command is being run.
    """
    with inside_dir(dirpath):
        return subprocess.check_call(shlex.split(command))


def check_output_inside_dir(command, dirpath):
    "Run a command from inside a given directory, returning the command output"
    with inside_dir(dirpath):
        return subprocess.check_output(shlex.split(command))


def project_info(result):
    """Get toplevel dir, project_slug, and project dir from baked cookies"""
    project_path = str(result.project)
    project_name = os.path.split(project_path)[-1]
    project_dir = os.path.join(project_path, project_name)
    return project_path, project_name, project_dir


@pytest.mark.parametrize(
    ("full_name"),
    (("Rodolfo Olivieri"),),
)
def test_year_compute_in_license_file(full_name, cookies):
    with bake_in_temp_dir(
        cookies,
        extra_context={"full_name": full_name},
    ) as result:
        license_file_path = result.project_path.joinpath("LICENSE")
        license_contents = license_file_path.read_text()
        now = datetime.datetime.now()
        assert str(now.year) in license_contents
        assert full_name in license_contents


@pytest.mark.parametrize(
    ("files_that_should_exist"),
    (
        (
            (
                "tox.ini",
                "setup.py",
                "setup.cfg",
                ".pre-commit-config.yaml",
                "cookiecutter_python_project",
                "requirements.dev.txt",
                "README.md",
                "LICENSE",
                ".github",
                ".git",
            )
        ),
    ),
)
def test_bake_with_defaults(files_that_should_exist, cookies):
    with bake_in_temp_dir(cookies) as result:
        assert result.project_path.is_dir()
        assert result.exit_code == 0
        assert result.exception is None

        found_toplevel_files = [f.name for f in result.project_path.iterdir()]
        for file in files_that_should_exist:
            assert file in found_toplevel_files


def test_bake_and_run_tests(cookies):
    with bake_in_temp_dir(cookies) as result:
        assert result.project_path.is_dir()
        major = sys.version_info.major
        minor = sys.version_info.minor
        tox_python_version = f"{major}{minor}"
        run_inside_dir(
            f"tox -e py{tox_python_version}",
            str(result.project_path),
        ) == 0
        print("test_bake_and_run_tests path", str(result.project_path))


@pytest.mark.parametrize(
    ("full_name"),
    (
        ('name "quote" name'),
        ("name name"),
        ("name 'single quote' name"),
        ("O'connor"),
    ),
)
def test_bake_withspecialchars_and_run_tests(full_name, cookies):
    """Ensure that a `full_name` with double quotes does not break setup.py"""
    with bake_in_temp_dir(
        cookies,
        extra_context={"full_name": full_name},
    ) as result:
        assert result.project_path.is_dir()
        major = sys.version_info.major
        minor = sys.version_info.minor
        tox_python_version = f"{major}{minor}"
        run_inside_dir(
            f"tox -e py{tox_python_version}",
            str(result.project_path),
        ) == 0


@pytest.mark.parametrize(
    ("license", "expected"),
    (
        ("MIT License", "MIT License"),
        (
            "BSD License",
            "Redistributions of source code must retain the above copyright "
            + "notice, this",
        ),
        ("ISC License", "ISC License"),
        (
            "Apache Software License 2.0",
            "Licensed under the Apache License, Version 2.0",
        ),
        ("GNU General Public License v3", "GNU GENERAL PUBLIC LICENSE"),
    ),
)
def test_bake_selecting_license(license, expected, cookies):
    with bake_in_temp_dir(
        cookies,
        extra_context={"open_source_license": license.strip()},
    ) as result:
        assert expected in result.project_path.joinpath("LICENSE").read_text()
        assert license in result.project_path.joinpath("setup.cfg").read_text()


def test_bake_not_open_source(cookies):
    with bake_in_temp_dir(
        cookies,
        extra_context={"open_source_license": "Not open source"},
    ) as result:
        found_toplevel_files = [f.name for f in result.project_path.iterdir()]
        assert "setup.cfg" in found_toplevel_files
        assert "LICENSE" not in found_toplevel_files


def test_project_with_hyphen_in_module_name(cookies):
    with bake_in_temp_dir(
        cookies,
        extra_context={"project_name": "something-with-a-dash"},
    ) as result:
        assert result.project is not None


@pytest.mark.parametrize(
    ("has_entrypoint", "expected"),
    (
        (
            "Yes, create entrypoint",
            "cookiecutter_python_project.main:main",
        ),
        (
            "No, skip entrypoint",
            "cookiecutter_python_project.main:main",
        ),
    ),
)
def test_bake_with_entrypoint_script(has_entrypoint, expected, cookies):
    with bake_in_temp_dir(
        cookies,
        extra_context={"has_entrypoint": has_entrypoint},
    ) as result:
        setup_cfg_contents = result.project_path.joinpath(
            "setup.cfg",
        ).read_text()
        if has_entrypoint == "Yes, create entrypoint":
            assert expected in setup_cfg_contents
        else:
            assert expected not in setup_cfg_contents


def test_pre_commit(cookies):
    with bake_in_temp_dir(cookies) as result:
        assert result.project_path.is_dir()
        assert (
            run_inside_dir(
                "pre-commit run --all-files",
                str(result.project_path),
            )
            == 0
        )


def test_has_correct_remote(cookies):
    with bake_in_temp_dir(
        cookies,
        extra_context={"project_name": "test"},
    ) as result:
        assert result.project_path.is_dir()
        remote = check_output_inside_dir(
            "git remote",
            str(result.project_path),
        )

        assert remote == b"origin\n"

        remote = check_output_inside_dir(
            "git remote show -n origin",
            str(result.project_path),
        )
        assert b"git@github.com:r0x0d/test\n"
