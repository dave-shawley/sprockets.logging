"""
logext: extensions to the standard logging module
=================================================

This module contains classes that work directly with the standard
:mod:`logging` module.  You should use this when configuring the
log layer either manually, via :func:`~logging.config.fileConfig` or
via :func:`~logging.config.dictConfig`.

- :class:`~.ContextFilter` adds properties to every log record so
  that you can safely refer to them in a format
- :class:`~JSONFormatter` formats log lines as JSON objects

"""
import json
import logging
import traceback
import warnings


class ContextFilter(logging.Filter):
    """
    Ensures that properties exist on a LogRecord.

    :param list properties: optional list of properties that
        will be added to LogRecord instances if they are missing
    :type properties: list or None

    This filter implementation will ensure that a set of properties
    exists on every log record which means that you can always refer
    to custom properties in a format string.  Without this, referring
    to a property that is not explicitly passed in will result in an
    ugly :exc:`KeyError` exception.

    """
    def __init__(self, name='', properties=None):
        logging.Filter.__init__(self, name)
        self.properties = list(properties) if properties else []

    def filter(self, record):
        """
        Overridden to add properties to `record`.

        :param logging.LogRecord record: the record to modify
        :returns: always returns :data:`True`

        """
        for property_name in self.properties:
            if not hasattr(record, property_name):
                setattr(record, property_name, None)
        return True


class JSONFormatter(logging.Formatter):
    """
    Format lines as JSON documents.

    This formatter dumps the log record as a JSON document.  It includes
    every attribute from the :class:`~logging.LogRecord` except for:

    - *dunder* attributes
    - :func:`callable` values
    - attributes that are special-cased:

      - the msg and args attributes are formatted with
        :meth:`~logging.LogRecord.getMessage`
      - the timestamp attribute is formatted with
        :meth:`~logging.Formatter.formatTime`
      - the exc_info attribute is transformed into an embedded document
        by calling :meth:`.extract_exc_record`

    This formatter is meant to be used with a :class:`.ContextFilter`
    to automatically add attributes to every logged message.

    """

    encoder = json.JSONEncoder(indent=0, separators=(',', ':'))
    """Class-level JSON encoder used to format records.

    This can be customized at the class-level as necessary.  The default is
    to minimize the representation by removing indentation as well as the
    spaces around separators.

    """

    _SPECIAL_CASES = frozenset({'msg', 'args', 'timestamp', 'exc_info'})

    @staticmethod
    def extract_exc_record(record):
        """
        Extract an exception record if one is present.

        :param logging.LogRecord record: log record to extract the
            traceback from
        :rtype: dict or None

        """
        try:
            typ, val, tb = record.exc_info
            return {
                'message': str(val),
                'stack': [{
                    'file': file_,
                    'func': func,
                    'line': str(line),
                    'text': text,
                } for file_, line, func, text in traceback.extract_tb(tb)],
                'type': typ.__name__,
            }
        except Exception:
            return None

    def _should_be_logged(self, name, value):
        """Should `name` and `value` be included in JSON document?"""
        return (name not in self._SPECIAL_CASES
                and not (name.startswith('__') and name.endswith('__'))
                and not callable(value))

    def format(self, record):
        """Return the log data as a JSON document

        :param logging.LogRecord record: The record to format
        :rtype: str

        """
        output = {
            'message': record.getMessage(),
            'timestamp': self.formatTime(record),
        }
        for name, value in record.__dict__.items():
            if self._should_be_logged(name, value):
                output[name] = value
        tb = self.extract_exc_record(record)
        if tb:
            output['traceback'] = tb
        return self.encoder.encode(output)


class JSONRequestFormatter(JSONFormatter):
    """
    Format lines as JSON documents.

    .. deprecated:: 2.0.0

       Please use :class:`JSONFormatter` instead.

    """
    def __init__(self, *args, **kwargs):
        warnings.warn(
            'sprockets_logging.logext.JSONRequestFormatter is deprecated'
            ' and will be removed in a future version', DeprecationWarning)
        super(JSONRequestFormatter, self).__init__(*args, **kwargs)
