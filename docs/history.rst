Version History
===============

`Next Release`_
---------------
*Complete reboot*

- Replace namespace packaging with ``sprockets_logging`` package
- Split single module into *logext* and *access* modules
- The JSON formatter now includes all properties of a ``LogRecord`` instead of 
  hard-coding a fixed set of them.
- Rename ``JSONRequestFormatter`` to ``JSONFormatter``.  The old name is
  deprecated.
- Add support for the `NCSA Common log format`_
- Make the JSON encoder instance customizable.
- Add support for specifying default values to ``ContextFilter``.

.. _NCSA Common log format: https://www.w3.org/Daemon/User/Config
   /Logging.html#common-logfile-format

`1.3.2`_ Oct  2, 2015
---------------------
- Switch to packaging as a package instead of a py_module.

`1.3.1`_ Sep 14, 2015
---------------------
- Fix query_arguments handling in Python 3

`1.3.0`_ Aug 28, 2015
---------------------
- Add the traceback and environment if set

`1.2.1`_ Jun 24, 2015
---------------------
- Fix a potential ``KeyError`` when a HTTP request object is not present.

`1.2.0`_ Jun 23, 2015
---------------------
 - Monkeypatch logging.currentframe
 - Include a logging message if it's there

`1.1.0`_ Jun 18, 2015
---------------------
 - Added ``sprockets.logging.JSONRequestFormatter``
 - Added ``sprockets.logging.tornado_log_function``
 - Added convenience constants and methods as a pass through to Python's logging package:

  - ``sprockets.logging.DEBUG`` to ``logging.DEBUG``
  - ``sprockets.logging.ERROR`` to ``logging.ERROR``
  - ``sprockets.logging.INFO`` to ``logging.INFO``
  - ``sprockets.logging.WARN`` to ``logging.WARN``
  - ``sprockets.logging.WARNING`` to ``logging.WARNING``
  - ``sprockets.logging.dictConfig`` to :func:`logging.config.dictConfig`
  - ``sprockets.logging.getLogger`` to :func:`logging.getLogger`

`1.0.0`_ Jun 09, 2015
---------------------
 - Added ``sprockets.logging.ContextFilter``

.. _Next Release: https://github.com/sprockets/sprockets.logging/compare/1.3.2...master

.. _1.3.2: https://github.com/sprockets/sprockets.logging/compare/1.3.1...1.3.2
.. _1.3.1: https://github.com/sprockets/sprockets.logging/compare/1.3.0...1.3.1
.. _1.3.0: https://github.com/sprockets/sprockets.logging/compare/1.2.1...1.3.0
.. _1.2.1: https://github.com/sprockets/sprockets.logging/compare/1.2.0...1.2.1
.. _1.2.0: https://github.com/sprockets/sprockets.logging/compare/1.1.0...1.2.0
.. _1.1.0: https://github.com/sprockets/sprockets.logging/compare/1.0.0...1.1.0
.. _1.0.0: https://github.com/sprockets/sprockets.logging/compare/0.0.0...1.0.0
