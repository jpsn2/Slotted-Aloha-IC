import os
import logging
from enum import Enum
from datetime import datetime

config = {"filename": "data/aloha.log", "level": logging.DEBUG}
logging.basicConfig(**config)


class Status(Enum):
    IDLE = "IDLE"
    SUCCESS = "SUCCESS"
    TRANSMITING = "TRANSMITING"
    GENERATING_PACKAGES = "GENERATING PACKAGES"
    PARTIAL_NODE_COLISION = "PARTIAL NODE COLISION + HEAD NODE SUCESS"
    HEAD_NODE_COLLISION = "HEAD_NODE COLLISION"
    NODE_COLLISION = "NODE COLLISION"
    GENERATING_HEAD_NODE = "GENERATING HEAD NODE"
    CONFIGURATION_NETWORK = "CONFIGURATION NETWORK"


def init_log():
    try:
        os.truncate(config["filename"], 0)
    except:
        pass


def log_line():
    message_log = "___________________________________"
    logging.info(message_log)


def log_info(network, node_index, status, currtime=None):
    log(network, node_index, status, logging.INFO, currtime)


def log(network, node_index, status, level=logging.DEBUG,time:float=None):
    if not time:
        message_log = "{timestamp},{network}, {node_index}, {event_type}, {message}, {time}".format(
            timestamp=datetime.now().isoformat(),
            network=network.network_name,
            node_index=node_index,
            event_type=status.name,
            message=status.value,
            time=None
        )
        logging.log(level, message_log)
    else:
        message_log = "{timestamp},{network}, {node_index}, {event_type}, {message}, {time}".format(
            timestamp=datetime.now().isoformat(),
            network=network.network_name,
            node_index=node_index,
            event_type=status.name,
            message=status.value,
            time=time
        )
        logging.log(level, message_log)
        


def custom_log(message_log, level=logging.INFO):
    logging.log(level, message_log)
