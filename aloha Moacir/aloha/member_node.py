import gc
import hashlib
import uuid
import random
from aloha.stack import Stack
from random import choice
from aloha.aloha_logging import log, log_info, custom_log, Status
from aloha.aloha_logging import Status
from aloha.network_node import NetWorkNode

class MemberNode(NetWorkNode):
    pilha: Stack
    time: int
    my_hash: int
    
    def __init__(self, main_network, node_index, generate_interval, transm_prob):
        super().__init__()
        self.Status = Status.IDLE
        self.main_network = main_network
        self.buffer = []
        self.id_list = []
        self.node_index = node_index
        self.generate_interval = generate_interval
        self.transmission_prob = transm_prob
        self.pilha = Stack()
        self.my_hash = 0
        self.time = 0
        self.status_head_node = Status.IDLE
        #self.share_id()
        
    def get_pilha(self):
        return self.pilha
        
    def set_left_node(self, left_node):
        self.left_node = left_node
        
    def set_right_node(self, right_node):
        self.right_node = right_node
    
    def get_left_node(self):
        return self.left_node
    
    def get_right_node(self):
        return self.right_node

    def generate(self, currtime):
        """
        Generate a new package
        """
        log(self.main_network, self.node_index, Status.GENERATING_PACKAGES, time=currtime)
        self.buffer.append(uuid.uuid4())
        self.get_pilha().clear()
        self.share_id()
        self.calculate_hash(currtime)
        self.calculate_all_hash(currtime)
            
    def calculate_hash(self, currtime):
        """
        Calculate the hash of the first element of the buffer
        """
        str_buffer = str(self.node_index) + self.main_network.network_name + str(currtime)
        my_hash = hashlib.sha256(str_buffer.encode()).hexdigest()
        int_hash = int(my_hash, 16)%100000001
        self.my_hash = int_hash
        self.get_pilha().push(self.my_hash)
        
    
    def calculate_all_hash(self, currtime):
        for id in self.id_list:
            if id != self.node_index:
                str_buffer = id + str(currtime)
                hash = hashlib.sha256(str_buffer.encode()).hexdigest()
                int_hash = int(hash, 16)%100000001
                if not self.get_pilha().contains(int_hash):
                    self.get_pilha().push(int_hash)
        self.get_pilha().sorted_stack()
    
    def clear(self):
        self.buffer = []
        gc.collect()

    def submit(self, currtime):
        """
        Send data to the network
        """    
        if self.get_pilha().length() > 0 and self.my_hash == self.get_pilha().get_head() and len(self.buffer) > 0 and self.status_head_node == Status.IDLE:
            log_info(self.main_network, self.node_index, Status.TRANSMITING, currtime=currtime)
            self.Status = Status.TRANSMITING
        else:               
            #log_info(self.main_network, self.node_index, Status.IDLE)
            self.Status = Status.IDLE
            self.get_pilha().clear()

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
            self.get_pilha().clear()
            #self.get_pilha().pop()

    def error(self):
        """
        Handle data when the transmission was
        collision
        """
        if self.Status == Status.TRANSMITING:
            self.Status = Status.IDLE
            self.clear()
            self.get_pilha().clear()
            #self.get_pilha().pop()

    def log_status(self):
        """
        Log Current Status
        """
        custom_log(f"MEMBER_NODE: {self.Status} {self.buffer}")
        
    def get_reserve(self):
        return self.reserve_slot
    
    def receive_id(self, id_list):
        self.id_list = id_list
    
    def share_id(self):
        self.main_network.head_node.receive_id_nodes(str(self.node_index) + self.main_network.network_name)

    def receive_status(self, status):
        self.status_head_node = status
    
    def __str__(self):
        return f"MemberNode {self.node_index}"