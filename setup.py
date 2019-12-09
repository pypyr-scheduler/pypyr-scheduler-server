from setuptools import setup, find_packages
from os import path
# import re

NAME = "pypyr-scheduler"

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

VERSION = "1.0.3"

setup(
    name=NAME,
    version=VERSION,
    description="Schedule pypyr pipelines with apscheduler and control them"
                "via REST. The API interface is provided by Zalando's"
                "connexion.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url="https://github.com/pypyr-scheduler/pypyr-scheduler",
    license='MIT',

    author='David Zerrenner',
    author_email="dazer017@gmail.com",

    classifiers=[
                 'Development Status :: 3 - Alpha',
                 'Intended Audience :: Developers',
                 "License :: OSI Approved :: MIT License",
                 "Programming Language :: Python",
                 "Programming Language :: Python :: 3.7",
    ],

    keywords=["OpenAPI", "Connexion", "Pypyr", "Scheduler", "Taskrunner"],

    packages=find_packages(exclude=['etc', 'var', 'junk']),
    package_data={'': ['conf/pypyr-scheduler.v1.yaml', 'conf/pypyr-scheduler.v1.without-pipelines.yaml', 'conf/pyrsched.ini', 'conf/scheduler_config.py', 'conf/logging_config.py',]},
    include_package_data=True,

    install_requires=[
        "connexion>=2.0.0",
        "swagger-ui-bundle>=0.0.2",
        "pyyaml>=5.2",
        "apscheduler>=3.6.3",
        "flask>=1.1.1",
        "flask-ini>=0.2.1",
        "pypyr>=3.0.2",
        "pytz>=2019.3",
        "apextras>=0.9.0",
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)
