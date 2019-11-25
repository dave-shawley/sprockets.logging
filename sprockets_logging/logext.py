import json
import logging
import traceback


class ContextFilter(logging.Filter):
    """
    Ensures that properties exist on a LogRecord.

    :param list|None properties: optional list of properties that
        will be added to LogRecord instances if they are missing

    This filter implementation will ensure that a set of properties
    exists on every log record which means that you can always refer
    to custom properties in a format string.  Without this, referring
    to a property that is not explicitly passed in will result in an
    ugly ``KeyError`` exception.

    """
    def __init__(self, name='', properties=None):
        logging.Filter.__init__(self, name)
        self.properties = list(properties) if properties else []

    def filter(self, record):
        for property_name in self.properties:
            if not hasattr(record, property_name):
                setattr(record, property_name, None)
        return True


class JSONRequestFormatter(logging.Formatter):
    """Instead of spitting out a "human readable" log line, this outputs
    the log data as JSON.

    """
    def extract_exc_record(self, typ, val, tb):
        """Create a JSON representation of the traceback given the records
        exc_info

        :param `Exception` typ: Exception type of the exception being handled
        :param `Exception` instance val: instance of the Exception class
        :param `traceback` tb: traceback object with the call stack

        :rtype: dict

        """
        exc_record = {'type': typ.__name__, 'message': str(val), 'stack': []}
        for file_name, line_no, func_name, txt in traceback.extract_tb(tb):
            exc_record['stack'].append({
                'file': file_name,
                'line': str(line_no),
                'func': func_name,
                'text': txt
            })
        return exc_record

    def format(self, record):
        """Return the log data as JSON

        :param record logging.LogRecord: The record to format
        :rtype: str

        """
        try:
            traceback = self.extract_exc_record(*record.exc_info)
        except:
            traceback = None

        output = {
            'name': record.name,
            'module': record.module,
            'message': record.msg % record.args,
            'level': logging.getLevelName(record.levelno),
            'line_number': record.lineno,
            'process': record.processName,
            'timestamp': self.formatTime(record),
            'thread': record.threadName,
            'file': record.filename,
            'request': record.args,
            'traceback': traceback
        }
        for key, value in list(output.items()):
            if not value:
                del output[key]
        if 'message' in output:
            output.pop('request', None)
        return json.dumps(output)
