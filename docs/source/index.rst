Plant IT
===================================

Plant IT empowers computational researchers to make their algorithms available
to a broad community, and provides biological researchers with an easy-to-use
interface to apply the algorithms to their own data.

.. toctree::
  :maxdepth: 2

  overview

Server Configuration
--------------------

.. toctree::
  :maxdepth: 2

  configuration

Plant IT Package
-----------------
The plantit package (`django/plantit/`) contains the back end code for the
website

.. toctree::
   :maxdepth: 3

   plantit

Front End APIs
----------------
The apis package (`django/apis/`) is build atop the django rest framework and
provides a bridge between the front-end code (`django/front-end`) and the back
end (`django/plantit`) code.

.. toctree::
  :maxdepth: 3

  apis

Front End Code
-----------------

.. toctree::
  :maxdepth: 1

  front_end_client_side

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
