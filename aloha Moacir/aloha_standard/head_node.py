from aloha.network_node import NetWorkNode
from aloha.aloha_logging import Status
from aloha.aloha_logging import *
from random import choice, random, uniform
import uuid
import os
import gc


class HeadNodeStandard(NetWorkNode):
    def __init__(self, main_network, subnet, coin, transm_prob):
        self.Status = Status.IDLE
        self.coin = coin
        self.main_network = main_network
        self.subnet = subnet
        self.buffer = []
        self.transmission_prob = transm_prob
        self.name = "Head Node"

    def generate(self):
        """
        Generate a new HeadNode
        """
        log(self.subnet, "HEAD_NODE", Status.GENERATING_HEAD_NODE)
        self.buffer.append(uuid.uuid4())

    def clear(self):
        self.buffer = []
        gc.collect()

    def submit(self, currtime):
        """
        Transmit data to main_network
        """
        if self.coin:
            submit_condition = (
                len(self.buffer) > 0
                and uniform(0, 1) <= self.transmission_prob
            )

        if submit_condition:
            log_info(self.subnet, "HEAD_NODE", Status.TRANSMITING, currtime=currtime)
            self.Status = Status.TRANSMITING
        else:
            log_info(self.subnet, "HEAD_NODE", Status.IDLE, currtime=currtime)
            self.Status = Status.IDLE

    def receive(self, data):
        """
        Receive data from the network
        """
        self.buffer += data

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
        custom_log(f"HEAD_NODE: {self.Status} {self.buffer}")
        
    def get_reserve(self):
        return self.reserve_slot