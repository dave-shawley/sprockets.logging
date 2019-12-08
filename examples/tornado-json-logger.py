import logging.config
import signal
import sys

from tornado import ioloop, web
from sprockets_logging import access, logext


def configure_logging():
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    root = logging.getLogger()
    root.handlers[0].formatter = logext.JSONFormatter()


class RequestHandler(web.RequestHandler):
    def get(self):
        status_code = self.get_query_argument('status', '200')
        self.set_status(int(status_code))
        if self.get_query_argument('fail', None):
            raise RuntimeError('injected failure')


def sig_handler(signo, frame):
    iol = ioloop.IOLoop.instance()
    iol.add_callback_from_signal(iol.stop)


if __name__ == '__main__':
    configure_logging()
    app = web.Application([web.url(r'/', RequestHandler)],
                          log_function=access.log_json)
    app.listen(8000)
    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)
    ioloop.IOLoop.instance().start()
