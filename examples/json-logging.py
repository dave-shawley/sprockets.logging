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
    logging.exception('Includes exception stack')
