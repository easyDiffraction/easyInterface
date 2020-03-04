.. image:: ./_static/easyInterface_logo.png
   :target: https::www.github.com/easyDiffraction/easyInterface

``easyInterface`` is a library to interface crystallographic calculators to front end applications, jupyter notebooks
and scripting interfaces.

=========================================
Welcome to easyInterface's documentation!
=========================================

The code of the project is on Github: `easyInterface <https://github.com/easyDiffraction/easyInterface>`_

Features of easyInterface
=========================

easyInterface is a way of storing information about crystal structures, providing commonly used functions in an easy to use package. The data structure interfaces to crystallographic libraries, making a common way to calculate observable phenomena regardless of your choice of backend calculator. Currently we support:

* `Cryspy <https://github.com/ikibalin/cryspy>`_ - a crystallographic library for neutron data analysis.

With more interfaces coming.


Projects using easyInterface
============================

easyInterface is currently being used in the following projects:

* `easyDiffraction <https://github.com/easyDiffraction/easyDiffraction>`_ - Scientific software for modelling and analysis of neutron diffraction data


Installation
============

Install via ``pip``
-------------------

You can do a direct install via pip by using:

.. code-block:: bash

    $ pip install easyInterface

Install as an easyInterface developer
-------------------------------------

You can get the latest development source from our `Github repository
<https://github.com/easyDiffraction/easyInterface>`_. You need
``setuptools`` installed in your system to install easyInterface. For example,
you can do:

.. code-block:: console

    $ git clone https://github.com/easyDiffraction/easyInterface
    $ cd easyInterface
    $ pip install -r requirements.txt
    $ pip install -e .

.. installation-end-content

Main Contents
------------------------------------------

.. toctree::
   :maxdepth: 2
   :caption: Example galleries

   auto_examples/index

.. toctree::
   :maxdepth: 1
   :caption: API and developer reference

   developer
   Fork easyInterface on Github <https://github.com/easyDiffraction/easyInterface>

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`