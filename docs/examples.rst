Examples
========

Simple Usage
------------
The following snippet uses :class:`sprockets_logging.logext.ContextFilter`
to insert context information into a message using a
:class:`logging.LoggerAdapter` instance.

.. literalinclude:: ../examples/simple.py

Dictionary-based Configuration
------------------------------
This package begins to shine if you use the dictionary-based logging
configuration offered by :func:`logging.config.dictConfig`.  You can insert
the custom filter and format string into the logging infrastructure and
insert context easily with :class:`logging.LoggerAdapter`.

.. literalinclude:: ../examples/tornado-app.py
   :emphasize-lines: 14,20,24-29,48,56,78

The ``contextual_access_logger`` function includes the context in the
Tornado access logs.  This example demonstrates the ability to specify
arbitrary default values for context values.  In this case, the context is
logged as ``-`` if the request does not contain a ``X-UniqID`` request
header.

Application JSON Logging
-------------------------
If you're looking to emit log application logs as JSON lines, the
:class:`sprockets_logging.logext.JSONFormatter` class works in conjunction with
the :func:`sprockets_logging.access.log_json` function to output all log records
as JSON objects.  The following example manually configures the logging module
to use a :class:`sprockets_logging.logext.JSONFormatter` instance as the
formatter and passes :func:`sprockets_logging.access.log_json` in as the
``log_function`` when creating the Tornado application.  The result is that
all logs are emitted as JSON documents.

.. literalinclude:: ../examples/tornado-json-logger.py

When you have the application running in a console and send a HTTP request to
it using *curl*, the following log line will be printed.  I reformatted it with
*jq* to make it more readable.

.. code-block:: json

   {
     "created": 1575814289.538684,
     "exc_text": null,
     "filename": "access.py",
     "funcName": "log_json",
     "levelname": "INFO",
     "levelno": 20,
     "lineno": 84,
     "message": "",
     "module": "access",
     "msecs": 538.6838912963867,
     "name": "tornado.access",
     "pathname": "/Users/daveshawley/Source/python/sprockets/sprockets.logging/sprockets_logging/access.py",
     "process": 74841,
     "processName": "MainProcess",
     "relativeCreated": 4874.499797821045,
     "stack_info": null,
     "thread": 4534386112,
     "threadName": "MainThread",
     "timestamp": "2019-12-08 09:11:29,538"
   }

All of the properties from the :class:`logging.LogRecord` are included as-is.
You can include the ``fail`` query parameter to inject a raised exception to
see that it also formats stack traces as a list of frames instead of a traceback.

.. code-block:: json
   :emphasize-lines: 21-38

   {
     "created": 1575814624.0152051,
     "exc_text": null,
     "filename": "web.py",
     "funcName": "log_exception",
     "levelname": "ERROR",
     "levelno": 40,
     "lineno": 1784,
     "message": "Uncaught exception GET /?fail=1 (127.0.0.1)\nHTTPServerRequest(protocol='http', host='127.0.0.1:8000', method='GET', uri='/?fail=1', version='HTTP/1.1', remote_ip='127.0.0.1')",
     "module": "web",
     "msecs": 15.205144882202148,
     "name": "tornado.application",
     "pathname": "/Users/daveshawley/Source/python/sprockets/sprockets.logging/env/lib/python3.8/site-packages/tornado/web.py",
     "process": 76938,
     "processName": "MainProcess",
     "relativeCreated": 27028.79524230957,
     "stack_info": null,
     "thread": 4659518912,
     "threadName": "MainThread",
     "timestamp": "2019-12-08 09:17:04,015",
     "traceback": {
       "message": "injected failure",
       "stack": [
         {
           "file": "/Users/daveshawley/Source/python/sprockets/sprockets.logging/env/lib/python3.8/site-packages/tornado/web.py",
           "func": "_execute",
           "line": "1697",
           "text": "result = method(*self.path_args, **self.path_kwargs)"
         },
         {
           "file": "examples/tornado-json-logger.py",
           "func": "get",
           "line": "20",
           "text": "raise RuntimeError('injected failure')"
         }
       ],
       "type": "RuntimeError"
     }
   }
