.. pypyr-scheduler documentation master file, created by
   sphinx-quickstart on Fri Nov 15 12:12:59 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pypyr-scheduler's documentation!
===========================================

Pypyr-Scheduler is a periodic task runner. It runs a set of
pypyr-pipelines periodically. Each pipeline can have its own
execution interval and other individual settings. 

Pypyr-Scheduler is built on `pypyr <https://github.com/pypyr/pypyr-cli>`_ 
and `apscheduler <https://apscheduler.readthedocs.io>`_.

The scheduler runs as own process and is controlled with a RPC client
(pypyr-scheduler-rpc-client). There is also a command line interface
(pypyr-scheduler-cli) for convenience. This documentation covers all three components.


.. toctree::
   :maxdepth: 3
   :caption: Contents:

   server
   cli
   rpc

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
