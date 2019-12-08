sprockets.logging
=================
Making logs nicer since 2015!

|Version| |Downloads| |Travis| |CodeCov| |ReadTheDocs|

Installation
------------
``sprockets_logging`` is available on the
`Python Package Index <https://pypi.python.org/pypi/sprockets_logging>`_
and can be installed via ``pip`` or ``easy_install``:

.. code-block:: bash

   pip install sprockets_logging

Documentation
-------------
https://sprocketslogging.readthedocs.org

Requirements
------------
-  No external requirements

Example
-------
This examples demonstrates using ``sprockets_logging`` to format log messages
as JSON documents.  Log aggregation for JSON documents has become a bit of a
standard since `docker started using them`_.  This extension plays nicely with
many aggregation frameworks.

.. code-block:: python

   import logging
   
   from sprockets_logging import logext
   
   logging.basicConfig(level=logging.INFO)
   formatter = logext.JSONFormatter()
   for handler in logging.getLogger().handlers:
       handler.setFormatter(formatter)
   
   logging.info('Hi there')
   try:
       raise RuntimeError('injected error')
   except RuntimeError:
       logging.exception('includes exception stack')

Running the example will output the following two JSON documents.

.. code-block:: json

   {
     "created": 1575816124.978444,
     "exc_text": null,
     "filename": "json-logging.py",
     "funcName": "<module>",
     "levelname": "INFO",
     "levelno": 20,
     "lineno": 10,
     "message": "Hi there",
     "module": "json-logging",
     "msecs": 978.4440994262695,
     "name": "root",
     "pathname": "examples/json-logging.py",
     "process": 85837,
     "processName": "MainProcess",
     "relativeCreated": 5.136251449584961,
     "stack_info": null,
     "thread": 4501110208,
     "threadName": "MainThread",
     "timestamp": "2019-12-08 09:42:04,978"
   }
   {
     "created": 1575816124.978633,
     "exc_text": null,
     "filename": "json-logging.py",
     "funcName": "<module>",
     "levelname": "ERROR",
     "levelno": 40,
     "lineno": 14,
     "message": "Includes exception stack",
     "module": "json-logging",
     "msecs": 978.632926940918,
     "name": "root",
     "pathname": "examples/json-logging.py",
     "process": 85837,
     "processName": "MainProcess",
     "relativeCreated": 5.325078964233398,
     "stack_info": null,
     "thread": 4501110208,
     "threadName": "MainThread",
     "timestamp": "2019-12-08 09:42:04,978",
     "traceback": {
       "message": "injected error",
       "stack": [
         {
           "file": "examples/json-logging.py",
           "func": "<module>",
           "line": "12",
           "text": "raise RuntimeError('injected error')"
         }
       ],
       "type": "RuntimeError"
     }
   }

Note that the second document includes a machine-readable version of a standard
python traceback.  This feature simplifies searching logs using something like
`JSONPath`_ or selecting fragments using `JSON Pointer`_.

The formatter uses a JSON encoder instance stored on the class to prevent
creating a new JSON encoder for each log message.  The encoder is configured
to minimize the representation by default.  You can customize it directly if
necessary:

.. code-block:: python

   from sprockets_logging import logext

   def safer_default_encoding(obj):
       if hasattr(obj, 'isoformat'):
          return obj.isoformat()
       return str(obj)


   logext.JSONFormatter.encoder.default = safer_default_encoding
   logext.JSONFormatter.encoder.indent = 2
   logext.JSONFormatter.encoder.item_separator = ', '
   logext.JSONFormatter.encoder.key_separator = ': '

.. _docker started using them: https://docs.docker.com/config/containers
   /logging/json-file/
.. _JSONPath: https://goessner.net/articles/JsonPath/
.. _JSON Pointer: https://tools.ietf.org/html/rfc6901

Source
------
``sprockets_logging`` source is available on Github at
`https://github.com/sprockets/sprockets.logging <https://github.com/sprockets/sprockets.logging>`_

License
-------
``sprockets_logging`` is released under the `3-Clause BSD license <https://github.com/sprockets/sprockets.logging/blob/master/LICENSE>`_.


.. |Version| image:: https://badge.fury.io/py/sprockets.logging.svg?
   :target: http://badge.fury.io/py/sprockets.logging
.. |Travis| image:: https://travis-ci.org/sprockets/sprockets.logging.svg?branch=master
   :target: https://travis-ci.org/sprockets/sprockets.logging
.. |CodeCov| image:: http://codecov.io/github/sprockets/sprockets.logging/coverage.svg?branch=master
   :target: https://codecov.io/github/sprockets/sprockets.logging?branch=master
.. |Downloads| image:: https://pypip.in/d/sprockets.logging/badge.svg?
   :target: https://pypi.python.org/pypi/sprockets.logging
.. |ReadTheDocs| image:: https://readthedocs.org/projects/sprocketslogging/badge/
   :target: https://sprocketslogging.readthedocs.org
