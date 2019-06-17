Plant IT
===================================

Plant IT Package
-----------------
The plant it package (`django/plantit/`) contains the back end code for the
website

.. toctree::
   :maxdepth: 2

   plantit

Front End APIs
----------------
The apis package (`django/apis/`) is build atop the django rest framework and
provides a bridge between the front-end code (`django/front-end`) and the back
end (`django/plantit`) code.

.. toctree::
  :maxdepth: 3

  apis

.. include:: urls.rst
.. include:: filesystems.rst
.. include:: settings.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
