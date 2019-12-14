import logging.config
import signal

from tornado import ioloop, log, web

LOG_CONFIG = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': 'simple',
            'filters': ['context'],
        },
    },
    'formatters': {
        'simple': {
            'class': 'logging.Formatter',
            'format': '%(levelname)s %(name)s: %(message)s [%(context)s]',
        },
    },
    'filters': {
        'context': {
            '()': 'sprockets_logging.logext.ContextFilter',
            'properties': {
                'context': '-'
            },
        },
    },
    'loggers': {
        'tornado': {
            'level': 'DEBUG',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
    'incremental': False,
}


class RequestHandler(web.RequestHandler):
    async def prepare(self):
        self.log_extra = {}
        logger = logging.getLogger('RequestHandler')
        self.logger = logging.LoggerAdapter(logger, extra=self.log_extra)

        maybe_future = super().prepare()
        if maybe_future:
            await maybe_future

        uniq_id = self.request.headers.get('X-UniqID')
        if uniq_id:
            self.log_extra['context'] = uniq_id

    def get(self, object_id):
        self.logger.debug('fetchin %s', object_id)
        self.set_status(200)
        return self.finish()


def contextual_access_logger(handler):
    """Injects the `log_extra` attribute of `handler` into access logs."""
    if handler.get_status() < 400:
        log_method = log.access_log.info
    elif handler.get_status() < 500:
        log_method = log.access_log.warning
    else:
        log_method = log.access_log.error
    request_time = 1000.0 * handler.request.request_time()
    log_method(
        "%d %s %.2fms",
        handler.get_status(),
        handler._request_summary(),
        request_time,
        extra=getattr(handler, 'log_extra', {}),
    )


def sig_handler(signo, frame):
    iol = ioloop.IOLoop.instance()
    iol.add_callback_from_signal(iol.stop)


if __name__ == '__main__':
    logging.config.dictConfig(LOG_CONFIG)
    logger = logging.getLogger('app')
    app = web.Application([web.url(r'/(?P<object_id>\w+)', RequestHandler)],
                          log_function=contextual_access_logger)
    app.listen(8000)
    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)
    ioloop.IOLoop.instance().start()
    logger.info('IO loop stopped, exiting')
