Development
===========

If your development environment is on Windows, these tips could be interesting.
First of all: try out `Windows Subsystem for Linux <https://docs.microsoft.com/en-us/windows/wsl>`_. It unites the best of both
worlds and makes it very easy to develop for both Linux and Windows.
Mileage may vary for MacOS, but you know what you are doing.

With this said: all of the following instructions or tips are 
tailored for a WSL or Linux environment.

Managing multiple python versions
---------------------------------

Development and testing for multiple python versions can be tedious. There are mainly
two tools you can use to take the edge off that:

pyenv
.....

``pyenv`` is able to manage multiple python installations for one user. 

tox
...

TBD, unsing ``tox`` for tests.

Managing the python environment
---------------------------

We recommend ``pipenv`` to manage the installed dependencies. 
