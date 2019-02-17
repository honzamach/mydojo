.. _section-deployment:

Deployment
================================================================================


Building package
--------------------------------------------------------------------------------

From the project`s root directory please execute following commands:

.. code-block:: shell

	(venv) $ make build-whl
	(venv) $ make deploy


Installation
--------------------------------------------------------------------------------


Installation from Python package
````````````````````````````````````````````````````````````````````````````````

.. note::

	This installation guide is not yet complete.

.. code-block:: shell

	pip3 install mydojo-*.whl --upgrade
	service apache2 restart
