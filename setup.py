from setuptools import setup
from os import path

NAME = "pypyr-scheduler"
VERSION = "2.0.0"

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name=NAME,
    version=VERSION,
    description="Schedule pypyr pipelines with apscheduler",
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

    keywords=["Pypyr", "Scheduler", "Taskrunner"],

    packages=['pyrsched'],
    include_package_data=True,

    install_requires=[
        "apscheduler",
        "pytz",
        "psutil",
        "click",
        "pypyr",
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)
