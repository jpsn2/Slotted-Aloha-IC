import gc
import uuid
import random
from random import choice
from aloha.aloha_logging import log, log_info, custom_log, Status
from aloha.aloha_logging import Status
from aloha.network_node import NetWorkNode

class MemberNodeStandard(NetWorkNode):
    def __init__(self, main_network, node_index, generate_interval, transm_prob):
        self.Status = Status.IDLE
        self.main_network = main_network
        self.buffer = []
        self.node_index = node_index
        self.generate_interval = generate_interval
        self.transmission_prob = transm_prob       
        self.time = 0

    def generate(self, currtime):
        """
        Generate a new package
        """   
        log(self.main_network, self.node_index, Status.GENERATING_PACKAGES, time=currtime)
        self.buffer = [uuid.uuid4()]
            

    def clear(self):
        self.buffer = []
        gc.collect()

    def submit(self, currtime):
        """
        Send data to the network
        """

        if (
            len(self.buffer) > 0
            and random.uniform(0, 1) <= self.transmission_prob
        ):
            log_info(self.main_network, self.node_index, Status.TRANSMITING, currtime=currtime)
            self.Status = Status.TRANSMITING

        else:
            log_info(self.main_network, self.node_index, Status.IDLE, currtime=currtime)

    def receive(self, data):
        """Receive data from the network"""
        pass

    def success(self):
        """
        Handle data when the transmission was
        success
        """
        if self.Status == Status.TRANSMITING:
            self.Status = Status.IDLE
            self.clear()

    def error(self):
        """
        Handle data when the transmission was
        collision
        """
        if self.Status == Status.TRANSMITING:
            self.Status = Status.IDLE

    def log_status(self):
        """
        Log Current Status
        """
        custom_log(f"MEMBER_NODE: {self.Status} {self.buffer}")
        
    def get_reserve(self):
        return self.reserve_slot