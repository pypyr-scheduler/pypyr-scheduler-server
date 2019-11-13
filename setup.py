from setuptools import setup, find_packages
from os import path
# import re

NAME = "pypyr-scheduler"

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

# with open(
#         path.join(
#             path.dirname(__file__),
#             'tiny_petstore', '__init__.py')) as v_file:
#     VERSION = re.compile(
#         r".*__version__ = '(.*?)'",
#         re.S).match(v_file.read()).group(1)

VERSION = "0.0.1"

setup(
    name=NAME,
    version=VERSION,
    description="Schedule pypyr pipelines with apscheduler and control them"
                "via REST. The API interface is provided by Zalando's"
                "connexion.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url="https://github.com/dzerrenner/pypyr-scheduler",
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
    package_data={'': ['conf/pypyr-scheduler.v1.yaml']},
    include_package_data=True,

    install_requires=[
        "connexion>=2.0.0",
        "swagger-ui-bundle>=0.0.2",
        # "python_dateutil==2.6.0",
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)
