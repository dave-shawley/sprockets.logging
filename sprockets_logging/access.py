"""
access: functions for formatting access logs
============================================

This module contains functions that format Tornado access logs in
various formats.  Each function is meant to be passed as the
``log_function`` keyword to the :class:`tornado.web.Application`
initializer.

"""
import logging
import os

import tornado.escape
import tornado.log


def log_json(handler):
    """
    Format access logs as JSON documents.

    :param tornado.web.RequestHandler handler: the handler that
        processed the request

    .. code:: python

       app = tornado.web.Application([('/', RequestHandler)],
                                     log_function=tornado_log_function)

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
