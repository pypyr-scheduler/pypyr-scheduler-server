import sys
import subprocess
from pathlib import Path
from rich import print
from pkg_resources import parse_version
from git.cmd import Git
from importlib import reload

TAB_LENGTH = 50
NAME = "pypyr-scheduler-server"
PYPI_URL = f"https://pypi.org/pypi/{NAME}/json"


def get_setup_version():
    return pyrsched.server.VERSION  # import is done in the main script while checking the correct working dir

def get_git_tag():
    g = Git(Path().resolve())
    return g.describe("--abbrev=0")

def get_pypi_version():
    import requests
    r = requests.get(PYPI_URL)
    pypi_version = r.json()["info"]["version"]
    return pypi_version

def get_versions():
    setup_version = parse_version(get_setup_version())
    print("Version stated in setup.py...".ljust(TAB_LENGTH), setup_version)

    tagged_version = parse_version(get_git_tag())
    print("Latest git tag...".ljust(TAB_LENGTH), tagged_version)
   
    pypi_version = parse_version(get_pypi_version())
    print("Newest version on pypi:".ljust(TAB_LENGTH), pypi_version)

    return setup_version, tagged_version, pypi_version


if __name__ == "__main__":
    print("Working dir:", Path().resolve())
    sys.path.insert(0, str(Path().parent.resolve()))
    try:
        import pyrsched.server
    except ModuleNotFoundError:
        print("[bold red]Could not import pyrsched.server.[/bold red]")
        print("This is most likely due to starting this script directly. Please use [bold]pipenv run release[/bold] instead.")
        print("Make sure that the working directory is the root directory of the package (where setup.py is located).")
        sys.exit(1)

    setup_version, git_version, pypi_version = get_versions()

    if pypi_version > setup_version and pypi_version > git_version:
        print("PyPI version is newest. [bold red]This is an inconsistent state.[/bold red] No automation implemented.")
        sys.exit(1)

    if setup_version > git_version:
        print("The version in setup.py is newest.")
        r = input("Tag the Repo? [Yn] ") or "Y"
        if r.upper() == "Y":
            # git pull, git tag, git push
            g = Git(Path().resolve())
            print("git pull... ", end=None)
            output = g.pull()
            print(output)
            print("Tagging local repo... ", end=None)
            output = g.tag("-a", setup_version, "-m", "automatic tag from release script")
            print(output)
            print("git push... ", end=None)
            output = g.push("--tags")
            print(output)
            setup_version, git_version, pypi_version = get_versions()
    
    if git_version > setup_version:
        print("The version in setup.py needs to be updated.")
        r = input("Update setup.py? [Yn] ") or "Y"
        if r.upper() == "Y":
            # the version is in fact stored in __init__.py of the package
            # we can replace this in memory because the file is only a few lines long
            package_init = []
            init_file = Path("pyrsched/server/__init__.py")
            with open(init_file, "r") as infile:
                while line := infile.readline():
                    if line.startswith("VERSION"):
                        line = f'VERSION = "{git_version}"\n'
                    package_init.append(line)
            with open(init_file, "w") as outfile:
                outfile.write("".join(package_init))
            reload(pyrsched.server)
            setup_version, git_version, pypi_version = get_versions()

    if pypi_version < setup_version:
        print("The package on PyPI needs to be updated.")
        r = input("Build Package and update on PyPI? [Yn] ") or "Y"
        if r.upper() == "Y":
            # clear dist directory
            dist_path = Path("dist").resolve()
            for f in dist_path.iterdir():
                f.unlink()
            
            # build package
            from setuptools.sandbox import run_setup
            run_setup("setup.py", ["sdist", "bdist_wheel"])

            # upload package
            from twine import cli
            from twine import exceptions

            try:
                twine_res = cli.dispatch(["upload", "dist/*"])
            except (exceptions.TwineException, requests.HTTPError) as exc:
                print("{}: {}".format(exc.__class__.__name__, exc.args[0]))

            print(f"Twine response: {twine_res}")
            setup_version, git_version, pypi_version = get_versions()

    print("all done...")