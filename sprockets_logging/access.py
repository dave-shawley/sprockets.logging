"""
access: functions for formatting access logs
============================================

This module contains functions that format Tornado access logs in
various formats.  Each function is meant to be passed as the
``log_function`` keyword to the :class:`tornado.web.Application`
initializer.

"""
import datetime
import logging
import os
import time

import tornado.escape
import tornado.log
import tornado.web


class AccessLogRecordingMixin(tornado.web.RequestHandler):
    """
    Mix this into a request handler to record additional information.

    This request handler mix-in is used in conjunction with the
    :func:`.common_log_format` access log function to record the number
    of response bytes written as well as the request start time.

    """
    def __init__(self, *args, **kwargs):
        self.request_start_time = time.time()
        self.response_bytes_written = 0
        super().__init__(*args, **kwargs)

    def flush(self, include_footers=False):
        """
        Extended to track the number of response bytes written.

        See :meth:`tornado.web.RequestHandler.flush` for the super-class
        documentation.

        """
        self.response_bytes_written += sum(
            len(chunk) for chunk in self._write_buffer)
        return super().flush(include_footers=include_footers)


def _extract_log_info(handler):
    """
    :param tornado.web.RequestHandler handler:
    :rtype: tuple[int,int,tornado.httputil.HTTPServerRequest,str]
    """
    status_code = handler.get_status()
    if status_code < 400:
        log_level = logging.INFO
    elif status_code < 500:
        log_level = logging.WARNING
    else:
        log_level = logging.ERROR

    request = handler.request
    start_time = getattr(handler, 'request_start_time',
                         getattr(request, '_start_time', 0.0))
    ts = datetime.datetime.fromtimestamp(start_time, datetime.timezone.utc)
    start_time = ts.strftime('%d/%b/%Y:%H:%M:%S %z')

    return status_code, log_level, request, start_time


def log_json(handler):
    """
    Format access logs as JSON documents.

    :param tornado.web.RequestHandler handler: the handler that
        processed the request

    **Example**

    .. code-block:: json

        {
            "correlation_id": null,
            "duration": 3.3241,
            "environment": null,
            "headers": {"Host": "127.0.0.1"},
            "method": "GET",
            "path": "/apache_pb.gif",
            "protocol": "http",
            "query_args": {},
            "remote_ip": "127.0.0.1",
            "status_code": 200
        }

    """
    status_code = handler.get_status()
    logger = tornado.log.access_log

    if status_code < 400:
        log_level = logging.INFO
    elif status_code < 500:
        log_level = logging.WARNING
    else:
        log_level = logging.ERROR
    correlation_id = (getattr(handler, 'correlation_id', None)
                      or handler.request.headers.get('Correlation-ID', None))
    logger.log(
        log_level, '', {
            'correlation_id': correlation_id,
            'duration': 1000.0 * handler.request.request_time(),
            'headers': dict(handler.request.headers),
            'method': handler.request.method,
            'path': handler.request.path,
            'protocol': handler.request.protocol,
            'query_args': tornado.escape.recursive_unicode(
                handler.request.query_arguments),
            'remote_ip': handler.request.remote_ip,
            'status_code': status_code,
            'environment': os.environ.get('ENVIRONMENT')
        })


def common_log_format(handler):
    """
    Log requests in the NCSA Common log format.

    :param tornado.web.RequestHandler handler: the request handler that
        processed the request

    This log format contains the following fields separated by spaces:

    +------------+-----------------------------------------------------------+
    | remotehost | The remote IP address that made the request.  No attempt  |
    |            | at reversing this to a DNS name is made.                  |
    +------------+-----------------------------------------------------------+
    | rfc931     | The remote "logname" of the user.  This is always "-".    |
    +------------+-----------------------------------------------------------+
    | authuser   | The authorized username.  This is derived from the        |
    |            | :attr:`~tornado.web.RequestHandler.current_user` attribute|
    |            | of the handler.  If this is unset, then "-" is used.      |
    +------------+-----------------------------------------------------------+
    | [date]     | The date and time that the request was received with a    |
    |            | resolution of one second.  The timestamp is formatted     |
    |            | using the following strftime format string:               |
    |            | ``[%d/%b/%Y:%H:%M:%S %z]``.                               |
    +------------+-----------------------------------------------------------+
    | "request"  | The request start line surrounded by double-quotes.  This |
    |            | is a reconstructed version of the first line of the       |
    |            | request which contains the request method, the URL path & |
    |            | query parameters, and the HTTP version separated by       |
    |            | spaces.                                                   |
    +------------+-----------------------------------------------------------+
    | status     | The response status code.                                 |
    +------------+-----------------------------------------------------------+
    | bytes      | The number of bytes sent in the response or "-" if        |
    |            | unavailable. You can mix the                              |
    |            | :class:`.AccessLogRecordingMixin` into your request       |
    |            | handler to capture this information.                      |
    +------------+-----------------------------------------------------------+

    **Example**
    ::

        127.0.0.1 user-identifier frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326

    See https://www.w3.org/Daemon/User/Config/Logging.html#common-logfile-format
    for the canonical definition of this log format.

    """  # noqa: E501
    status_code, log_level, request, start_time = _extract_log_info(handler)
    tornado.log.access_log.log(
        log_level,
        '%s - %s [%s] "%s %s %s" %s %s',
        request.remote_ip or '-',
        handler.current_user or '-',
        start_time,
        request.method,
        request.uri,
        request.version,
        status_code,
        getattr(handler, 'response_bytes_written', '-'),
    )


def combined_log_format(handler):
    """
    Log requests in the Apache "combined" log format.

    :param tornado.web.RequestHandler handler: the request handler that
        processed the request

    This log format contains the same fields as the :func:`.common_log_format`
    with two additional quoted string fields appended:

    - the value of the :http:header:`Referer` header
    - the value of the :http:header:`User-Agent` header
    
    **Example**
    ::
    
        127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326 "http://www.example.com/start.html" "Mozilla/4.08 [en] (Win98; I ;Nav)"

    See http://httpd.apache.org/docs/2.2/logs.html#combined for the
    canonical definition of this log format.

    """  # noqa: E501
    status_code, log_level, request, start_time = _extract_log_info(handler)
    tornado.log.access_log.log(
        log_level,
        '%s - %s [%s] "%s %s %s" %s %s "%s" "%s"',
        request.remote_ip or '-',
        handler.current_user or '-',
        start_time,
        request.method,
        request.uri,
        request.version,
        status_code,
        getattr(handler, 'response_bytes_written', '-'),
        request.headers.get('Referer', '-'),
        request.headers.get('User-Agent', '-'),
    )
