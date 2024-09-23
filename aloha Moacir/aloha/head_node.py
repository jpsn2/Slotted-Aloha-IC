import hashlib
from aloha.network_node import NetWorkNode
from aloha.aloha_logging import Status
from aloha.aloha_logging import *
from random import choice, random, uniform
from aloha.stack import Stack
import uuid
import os
import gc


class HeadNode(NetWorkNode):
    pilha: Stack

    def __init__(self, main_network, subnet, coin, transm_prob):
        self.Status = Status.IDLE
        self.coin = coin
        self.main_network = main_network
        self.subnet = subnet
        self.buffer = []
        self.id_list = []
        self.name = "Head Node"
        self.transmission_prob = transm_prob
        self.pilha = Stack()
        self.my_hash = 0
        #self.reserve_slot = choice([True, False])

    def get_pilha(self):
        return self.pilha

    def generate(self, currtime):
        """
        Generate a new package
        """
        log(self.subnet, "HEAD_NODE", Status.GENERATING_HEAD_NODE)
        self.buffer.append(uuid.uuid4())
        self.get_pilha().clear()
        self.share_id()
        self.calculate_hash(currtime)
        self.calculate_all_hash(currtime)

    def clear(self):
        self.buffer = []
        gc.collect()

    def submit(self, currtime):
        """
        Transmit data to main_network
        """
        self.get_pilha().clear()
        self.share_id()     
        self.calculate_hash(currtime)
        self.calculate_all_hash(currtime)
        if self.coin:
            submit_condition = len(self.buffer) > 0
        
        if submit_condition and self.my_hash == self.get_pilha().get_head():
            log_info(self.subnet, "HEAD_NODE", Status.TRANSMITING, currtime=currtime)
            self.Status = Status.TRANSMITING
        else:
            #log_info(self.subnet, "HEAD_NODE", Status.IDLE, currtime=currtime)
            self.get_pilha().clear()
            #self.Status = Status.IDLE

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
        self.get_pilha().clear()

    def error(self):
        """
        Handle data when the transmission was
        collision
        """
        if self.Status == Status.TRANSMITING:
            self.Status = Status.IDLE
            self.clear()
        self.get_pilha().clear()

    def log_status(self):
        """
        Log Current Status
        """
        custom_log(f"HEAD_NODE: {self.Status} {self.buffer}")
        
    def get_reserve(self):
        return self.reserve_slot
    
    def receive_id_nodes(self, id):
        if not id in self.id_list:
            self.id_list.append(id)
        self.share_id()

    def share_id(self):
        for node in self.subnet.members:
            node.receive_id(self.id_list)
    
    def calculate_hash(self, currtime):
        """
        Calculate the hash of the first element of the buffer
        """
        str_buffer = str(currtime) + self.subnet.network_name
        my_hash = hashlib.sha256(str_buffer.encode()).hexdigest()
        int_hash = int(my_hash, 16)%100000001
        self.my_hash = int_hash
        self.get_pilha().push(self.my_hash)
    
    def calculate_all_hash(self, currtime):
        for id in self.main_network.members:
            if id.subnet.network_name != self.subnet.network_name:
                str_buffer = str(currtime) + id.subnet.network_name
                hash = hashlib.sha256(str_buffer.encode()).hexdigest()
                int_hash = int(hash, 16)%100000001
                if not self.get_pilha().contains(int_hash):
                    self.get_pilha().push(int_hash)
        self.get_pilha().sorted_stack()

    def __str__(self):
        return "Head Node"