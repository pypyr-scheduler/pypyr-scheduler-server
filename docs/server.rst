pypyr-scheduler-server
======================

This is the main part where all the work is done.

Prerequisites
-------------

APScheduler needs a database (the job store) to store information about
the state of the scheduled Jobs. The default with pypyr-scheduler is
in memory which is not very useful, because all jobs will be gone
if the server process is stopped. Among all possible options APScheduler has
(see its `docs <https://apscheduler.readthedocs.io/en/stable/userguide.html>`_),
sqlite is absolutely sufficient until you are running thousands of jobs.


Installation
------------

The recommended way is to use `pipenv <https://pipenv.pypa.io/en/latest/>`_::


    pipenv install pypyr-scheduler-server

The RPC client and the command line interface can be installed seperately::

    pipenv install pypyr-scheduler-rpc-client
    pipenv install pypyr-scheduler-cli

Alternatively, you can also use ``pip`` to install the package.

Configuration
-------------

There is one configuration file (default location: ``conf/scheduler_config.py``) which controls
the scheduler, pypyr and logging. In the configuration file, there are there
python dictionaries defined, one for each of the sections above.

``apscheduler`` is a apschedulers configuration and is passed as-is to it
at server startup. See `apscheduler's documentation <https://apscheduler.readthedocs.io/en/stable/userguide.html#configuring-the-scheduler>`_
for details. "Method 2" is used.

``pypyr`` controls pypyr and other aspects of the sheduler::

    pypyr = {
        'pipelines.base_path': 'pipelines',
        'pipelines.log_path': 'logs',
        'pipelines.log_level': logging.INFO,
        'server_port': 12345,
    }

Note that there is only a port configuration, no host. The server will always
listen on ``localhost`` for security reasons. If you want to connect from outside,
you'll have to tunnel a connection. 

Running the server
------------------

Run the server with::

    pipenv run server