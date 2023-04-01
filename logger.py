import logging

server_logger = logging.getLogger('ServerLogger')
server_logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

handler.setFormatter(formatter)
server_logger.addHandler(handler)
