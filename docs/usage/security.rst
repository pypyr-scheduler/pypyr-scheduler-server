Security
========

Pypyr-Scheduler does not include any security measures
at all. This is deliberate, since there are way too many
different ways to implment it. 

`Connexion's documentation <https://connexion.readthedocs.io/en/latest/security.html>`_ has
some instructions how to implement authentication measures. 
This could be a good starting point to get going. Basically,
you'll want to modify the API specification (located in ``conf/pypyr-scheduler.v1-yaml``) 
and put pointers to your authentication Methods in there.

With that said, you probably don't want to give the 
directory with your pipelines public access. 

.. note::
   Per default, the API portion starting with
   ``/pipelines`` is **disabled**. To enable it, use the 
   option ``--enable-upload``.

