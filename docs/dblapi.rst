API Reference
===============

The following section outlines the API of dblapi.

.. note::

    This module uses the Python logging module to log diagnostic and errors
    in an output independent way.  If the logging module is not configured,
    these logs will not be output anywhere.

Version Related Info
---------------------

There are two main ways to query version information about the library.

.. data:: version_info

    A named tuple that is similar to `sys.version_info`_.

    Just like `sys.version_info`_ the valid values for ``releaselevel`` are
    'alpha', 'beta', 'candidate' and 'final'.

    .. _sys.version_info: https://docs.python.org/3.6/library/sys.html#sys.version_info

.. data:: __version__

    A string representation of the version. e.g. ``'0.1.0-alpha0'``.

Client
--------------------

.. automodule:: dblapi.client
    :members:

Models
---------------------------

Here is collection of models used by dblapi.

DBLBot
~~~~~~~

.. autoclass:: dblapi.data_objects.DBLBot
    :members:

Avatar
~~~~~~~

.. autoclass:: dblapi.data_objects.Avatar
    :members:

Description
~~~~~~~~~~~~

.. autoclass:: dblapi.data_objects.Description
    :members:

DBLStats
~~~~~~~~~

.. autoclass:: dblapi.data_objects.DBLStats
    :members:



Exceptions
--------------------

.. automodule:: dblapi.errors
    :members:
    :undoc-members:
    :show-inheritance:

