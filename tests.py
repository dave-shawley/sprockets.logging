import collections
import contextlib
import datetime
import json
import logging
import os
import unittest
import urllib.parse
import uuid
import warnings

from tornado import web, testing

from sprockets_logging import access, logext


def setup_module():
    os.environ.setdefault('ENVIRONMENT', 'development')
    warnings.simplefilter('default')
    os.environ['PYTHONWARNINGS'] = 'default'


class SimpleHandler(web.RequestHandler):
    def get(self):
        if self.get_query_argument('runtime_error', default=None):
            raise RuntimeError(self.get_query_argument('runtime_error'))
        if self.get_query_argument('status_code', default=None) is not None:
            self.set_status(int(self.get_query_argument('status_code')))
        else:
            self.set_status(204)


class AugmentedHandler(access.AccessLogRecordingMixin, web.RequestHandler):
    def get(self):
        self.current_user = self.get_query_argument('user', default=None)
        self.write(
            os.urandom(int(self.get_query_argument('num_bytes', default='0'))))
        self.set_status(200)


class RecordingHandler(logging.Handler):
    def __init__(self):
        super(RecordingHandler, self).__init__()
        self.emitted = []

    def emit(self, record):
        self.emitted.append((record, self.format(record)))


class TornadoLoggingTestMixin(unittest.TestCase):
    def setUp(self):
        super(TornadoLoggingTestMixin, self).setUp()
        self.access_log = logging.getLogger('tornado.access')
        self.app_log = logging.getLogger('tornado.application')
        self.gen_log = logging.getLogger('tornado.general')
        for logger in (self.access_log, self.app_log, self.gen_log):
            logger.disabled = False

        self.recorder = RecordingHandler()
        root_logger = logging.getLogger()
        root_logger.addHandler(self.recorder)

    def tearDown(self):
        super(TornadoLoggingTestMixin, self).tearDown()
        logging.getLogger().removeHandler(self.recorder)


class TornadoLogFunctionTests(TornadoLoggingTestMixin,
                              testing.AsyncHTTPTestCase):
    def get_app(self):
        return web.Application([web.url('/', SimpleHandler)],
                               log_function=access.log_json)

    @property
    def access_record(self):
        for record, _ in self.recorder.emitted:
            if record.name == 'tornado.access':
                return record

    def test_that_redirect_logged_as_info(self):
        self.fetch('?status_code=303')
        self.assertEqual(self.access_record.levelno, logging.INFO)

    def test_that_client_error_logged_as_warning(self):
        self.fetch('?status_code=400')
        self.assertEqual(self.access_record.levelno, logging.WARNING)

    def test_that_exception_is_logged_as_error(self):
        self.fetch('/?runtime_error=something%20bad%20happened')
        self.assertEqual(self.access_record.levelno, logging.ERROR)

    def test_that_log_includes_correlation_id(self):
        self.fetch('/?runtime_error=something%20bad%20happened')
        self.assertIn('correlation_id', self.access_record.args)

    def test_that_log_includes_duration(self):
        self.fetch('/?runtime_error=something%20bad%20happened')
        self.assertIn('duration', self.access_record.args)

    def test_that_log_includes_headers(self):
        self.fetch('/?runtime_error=something%20bad%20happened')
        self.assertIn('headers', self.access_record.args)

    def test_that_log_includes_method(self):
        self.fetch('/?runtime_error=something%20bad%20happened')
        self.assertEqual(self.access_record.args['method'], 'GET')

    def test_that_log_includess_path(self):
        self.fetch('/?runtime_error=something%20bad%20happened')
        self.assertEqual(self.access_record.args['path'], '/')

    def test_that_log_includes_protocol(self):
        self.fetch('/?runtime_error=something%20bad%20happened')
        self.assertEqual(self.access_record.args['protocol'], 'http')

    def test_that_log_includes_query_arguments(self):
        self.fetch('/?runtime_error=something%20bad%20happened')
        self.assertEqual(self.access_record.args['query_args'],
                         {'runtime_error': ['something bad happened']})

    def test_that_log_includes_remote_ip(self):
        self.fetch('/?runtime_error=something%20bad%20happened')
        self.assertIn('remote_ip', self.access_record.args)

    def test_that_log_includes_status_code(self):
        self.fetch('/?runtime_error=something%20bad%20happened')
        self.assertEqual(self.access_record.args['status_code'], 500)

    def test_that_log_includes_environment(self):
        self.fetch('/?runtime_error=something%20bad%20happened')
        self.assertEqual(self.access_record.args['environment'],
                         os.environ['ENVIRONMENT'])

    def test_that_log_includes_correlation_id_from_header(self):
        cid = str(uuid.uuid4())
        self.fetch('/?runtime_error=something%20bad%20happened',
                   headers={'Correlation-ID': cid})
        self.assertEqual(self.access_record.args['correlation_id'], cid)


class JSONFormatterTests(TornadoLoggingTestMixin, testing.AsyncHTTPTestCase):
    def setUp(self):
        super(JSONFormatterTests, self).setUp()
        self.formatter = logext.JSONFormatter()
        self.recorder.setFormatter(self.formatter)

    def get_app(self):
        return web.Application([web.url('/', SimpleHandler)],
                               log_function=access.log_json)

    def get_log_line(self, log_name):
        for record, line in self.recorder.emitted:
            if record.name == log_name:
                return json.loads(line)

    def test_that_messages_are_json_encoded(self):
        self.fetch('/')
        for _, line in self.recorder.emitted:
            json.loads(line)

    def test_that_exception_has_traceback(self):
        self.fetch('/?runtime_error=foo')
        entry = self.get_log_line('tornado.application')
        self.assertIsNotNone(entry.get('traceback'))
        self.assertNotEqual(entry['traceback'], [])

    def test_that_successes_do_not_have_traceback(self):
        self.fetch('/')
        for _, line in self.recorder.emitted:
            entry = json.loads(line)
            self.assertNotIn('traceback', entry)

    def test_that_special_case_attributes_are_not_included(self):
        self.fetch('/')
        for _, line in self.recorder.emitted:
            entry = json.loads(line)
            for name in {'args', 'msg', 'exc_info'}:
                self.assertNotIn(name, entry)
            for name in entry.keys():
                self.assertFalse(name.startswith('__') and name.endswith('__'))

    def test_that_special_case_attributes_are_correctly_handled(self):
        self.fetch('/')
        for record, line in self.recorder.emitted:
            entry = json.loads(line)
            self.assertEqual(entry['message'], record.getMessage())
            self.assertEqual(entry['timestamp'],
                             self.formatter.formatTime(record))

    def test_that_encoder_defaults_minimizes_encoding(self):
        self.assertEqual(logext.JSONFormatter.encoder.indent, 0)
        self.assertEqual(logext.JSONFormatter.encoder.item_separator, ',')
        self.assertEqual(logext.JSONFormatter.encoder.key_separator, ':')

    def test_that_json_encoding_can_be_customized(self):
        logext.JSONFormatter.encoder.indent = 0
        logext.JSONFormatter.encoder.item_separator = ',  '
        logext.JSONFormatter.encoder.key_separator = ':  '
        self.fetch('/')
        for _, line in self.recorder.emitted:
            self.assertNotIn('"message":"",', line)
            self.assertIn('"message":  "",  ', line)


class ContextFilterTests(TornadoLoggingTestMixin, unittest.TestCase):
    def setUp(self):
        super(ContextFilterTests, self).setUp()
        self.filter = logext.ContextFilter(properties=['correlation_id'])
        self.logger = logging.getLogger('test-logger')
        self.recorder.setFormatter(
            logging.Formatter('%(message)s {CID %(correlation_id)s}'))
        self.recorder.addFilter(self.filter)

    def test_that_property_is_set_to_none_by_filter_when_missing(self):
        self.logger.error('error message')
        _, line = self.recorder.emitted[0]
        self.assertEqual(line, 'error message {CID None}')

    def test_that_extras_property_is_used(self):
        self.logger.error('error message',
                          extra={'correlation_id': 'CORRELATION-ID'})
        _, line = self.recorder.emitted[0]
        self.assertEqual(line, 'error message {CID CORRELATION-ID}')

    def test_that_property_from_logging_adapter_works(self):
        cid = uuid.uuid4()
        logger = logging.LoggerAdapter(self.logger, {'correlation_id': cid})
        logger.error('error message')
        _, line = self.recorder.emitted[0]
        self.assertEqual(line, 'error message {CID %s}' % cid)

    def test_that_default_values_can_be_specified(self):
        self.filter.properties = {'correlation_id': '-'}
        self.logger.error('error message')
        _, line = self.recorder.emitted[0]
        self.assertEqual(line, 'error message {CID -}')

    def test_that_setting_properties_to_none_clears_property_set(self):
        self.filter.properties = None
        self.assertDictEqual({}, self.filter.properties)


class DeprecatedTestCases(unittest.TestCase):
    @contextlib.contextmanager
    def assert_deprecation_message(self, message):
        with self.assertWarns(DeprecationWarning) as context:
            yield
        for warning_msg in context.warnings:
            if message in str(warning_msg.message):
                return
        self.fail(f'expected deprecation warning {message}')

    def test_that_json_request_formatter_is_deprecated(self):
        with self.assert_deprecation_message(
                'JSONRequestFormatter is deprecated'):
            logext.JSONRequestFormatter()


ParsedCommonLog = collections.namedtuple(
    'ParsedCommonLog',
    ('remote_ip', 'user_id', 'current_user', 'timestamp', 'method', 'url',
     'http_version', 'status_code', 'response_size'))


class CommonLogFormatTests(TornadoLoggingTestMixin, testing.AsyncHTTPTestCase):
    _parsed_log_line = None

    def get_app(self):
        handlers = [
            web.url(r'/augmented', AugmentedHandler),
            web.url(r'/simple', SimpleHandler),
        ]
        return web.Application(handlers, log_function=access.common_log_format)

    @property
    def access_record(self):
        for record, _ in self.recorder.emitted:
            if record.name == 'tornado.access':
                return record

    @property
    def parsed_log_line(self):
        if self._parsed_log_line is None:
            parts = self.access_record.message.split()
            self.assertEqual(len(parts), 10)
            self._parsed_log_line = ParsedCommonLog(
                parts[0], parts[1], parts[2],
                (parts[3][1:] + ' ' + parts[4][:-1]), parts[5][1:], parts[6],
                parts[7][:-1], parts[8], parts[9])
        return self._parsed_log_line

    def test_that_redirect_logged_as_info(self):
        self.fetch('/simple?status_code=303')
        self.assertEqual(self.access_record.levelno, logging.INFO)

    def test_that_client_error_logged_as_warning(self):
        self.fetch('/simple?status_code=400')
        self.assertEqual(self.access_record.levelno, logging.WARNING)

    def test_that_exception_is_logged_as_error(self):
        self.fetch('/simple?runtime_error=something%20bad%20happened')
        self.assertEqual(self.access_record.levelno, logging.ERROR)

    def test_that_all_fields_are_included(self):
        before_start = datetime.datetime.now(datetime.timezone.utc)
        request_url = self.get_url('/simple')
        self.fetch(request_url)
        after_end = datetime.datetime.now(datetime.timezone.utc)

        request_url = urllib.parse.urlsplit(request_url)
        self.assertEqual(self.parsed_log_line.remote_ip, request_url.hostname)
        self.assertEqual(self.parsed_log_line.user_id, '-')
        self.assertEqual(self.parsed_log_line.current_user, '-')
        # self.assertEqual(self.parsed_log_line.timestamp, '')  see below
        self.assertEqual(self.parsed_log_line.method, 'GET')
        self.assertEqual(self.parsed_log_line.url, request_url.path)
        self.assertEqual(self.parsed_log_line.http_version, 'HTTP/1.1')
        self.assertEqual(self.parsed_log_line.status_code, '204')
        self.assertEqual(self.parsed_log_line.response_size, '-')

        # trim sub-second values off of before_start & after_end since the
        # access log does not include sub-second details
        before_start = before_start.replace(microsecond=0)
        after_end = after_end.replace(microsecond=0)
        parsed_timestamp = datetime.datetime.strptime(
            self.parsed_log_line.timestamp,
            '%d/%b/%Y:%H:%M:%S %z',
        )
        self.assertTrue(
            before_start <= parsed_timestamp <= after_end,
            f'expected {parsed_timestamp} to be between '
            f'{before_start} and {after_end}')

    def test_augmented_handler_details(self):
        request_url = self.get_url('/augmented?num_bytes=100&user=me')
        self.fetch(request_url)

        self.assertEqual(self.parsed_log_line.user_id, '-')
        self.assertEqual(self.parsed_log_line.current_user, 'me')
        self.assertEqual(self.parsed_log_line.response_size, '100')
