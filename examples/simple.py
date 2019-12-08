import logging
import sys

from sprockets_logging import logext

logging.basicConfig(stream=sys.stdout,
                    level=logging.DEBUG,
                    format='%(levelname)s %(message)s {%(context)s}')
root = logging.getLogger()
root.handlers[0].addFilter(logext.ContextFilter(properties=['context']))

# Outputs: INFO Hi there {None}
logging.info('Hi there')

# Outputs: INFO No KeyError {bah}
logging.info('No KeyError', extra={'context': 'bah'})

# Outputs: INFO Now with context! {foo}
adapted = logging.LoggerAdapter(logging.Logger.root, extra={'context': 'foo'})
adapted.info('Now with context!')
