from concurrent.futures import ThreadPoolExecutor
import gc
import time
import threading
from typing import List
from aloha.head_node import HeadNode
from aloha.aloha_utils import flatten
from aloha.aloha_logging import Status
from aloha.member_node import MemberNode
from aloha.aloha_logging import Status, log_info, log, log_line
from alive_progress import alive_bar
import random

from aloha_standard.member_node import MemberNodeStandard

class Network:
    network_name: str
    head_node: HeadNode
    members: List[MemberNode]

    def __init__(self, name, nodes_per_subnet, generate_interval, packets, head_node_generate, updates):
        self.network_name = name
        self.members = []
        self.memory = []
        self.slot_enlace = nodes_per_subnet * (2 + generate_interval) * (generate_interval ** 2) + 1
        self.packets = packets
        self.nodes_per_subnet = nodes_per_subnet
        self.head_node_generate = head_node_generate
        self.generate_interval = generate_interval
        self.updates = updates

    def get_status(self):
        return {
            "network_name": self.network_name,
            "buffer": self.buffer,
            "memory": self.memory,
            "members": self.members
        }

    def get_transmitting_nodes(self):
        return [node for node in self.members if node.Status == Status.TRANSMITING]

    @property
    def buffer(self):
        buffers = [node.buffer for node in self.get_transmitting_nodes()]
        return flatten(buffers)

    def get_submission_status(self):
        """
        Validate if more then one network node was sedded data
        """       
        transmitting_nodes = self.get_transmitting_nodes()
        if self.updates:
            for node in transmitting_nodes:
                if type(node) is HeadNode:
                    print(str(node.__str__()) + " | " + str(node.subnet.network_name) + "\n")
                else:
                    print(str(node.__str__()) + " | " + str(node.get_pilha()) + " | " + str(node.main_network.network_name) + "\n")
        if hasattr(self, "head_node"):
            # Member and head collision
            if (
                len(transmitting_nodes) >= 1
                and self.head_node.Status == Status.TRANSMITING
            ):
                log_info(self, None, Status.PARTIAL_NODE_COLISION)
                return Status.PARTIAL_NODE_COLISION

        # Member collision
        if len(transmitting_nodes) > 1:
            log_info(self, None, Status.NODE_COLLISION)
            return Status.NODE_COLLISION

        if len(transmitting_nodes) == 0:
            log_info(self, None, Status.IDLE)
            return Status.IDLE

        if len(transmitting_nodes) == 1:
            log_info(self, None, Status.SUCCESS)
            return Status.SUCCESS

    def notify_collision(self, collision_type):
        """
        Notify all members when a collision occours
        """
        transmitting_nodes = self.get_transmitting_nodes()

        for node in transmitting_nodes:
            node.error()

    def notify(self, status, currtime):
        log(self, None, status, time=currtime)
        if status in [
            Status.NODE_COLLISION,
            Status.PARTIAL_NODE_COLISION,
        ]:
            self.notify_collision(status)
            print("COLLISION" + " | " + self.network_name)
        elif status == Status.SUCCESS:
            self.notify_success()
            print("SUCCESS" + " | " + self.network_name)

    def notify_success(self):
        """
        Notify all members when a transmission have success
        """
        if hasattr(self, "head_node"):
            self.head_node.receive(self.buffer)

        self.memory += flatten([self.buffer])

        for node in self.members:
            node.success()

    def clear(self):
        """
        Clear network buffer
        """
        self.memory = []
        gc.collect()

    def set_slot_enlace(self, slot_enlace):
        self.slot_enlace = slot_enlace
        
    def get_slot_enlace(self):
        return self.slot_enlace
    
    def get_packates(self):
        return self.packets
    
    def generate_packets(self, currtime, subnet):
        #for subnet in subnet_list:
        if subnet.head_node_generate:
            subnet.head_node.generate(currtime)       
        for node_index in range(self.nodes_per_subnet):
            if node_index < len(subnet.members):
                subnet.members[node_index].generate(currtime)
            else:
                print(f"Erro: node_index {node_index} fora do intervalo. Tamanho da lista: {len(subnet.members)}")

        log_line()
    
    def execute_thread(self, generate_packets, slot_index, subnet_list):
        time_sleep = random.randint(1, 100) / 10000
        with ThreadPoolExecutor(max_workers=4) as executor:
            for subnet in subnet_list:
                # Submete as tarefas para gerar pacotes em paralelo
                """ future_0 = executor.submit(generate_packets, slot_index, subnet_list[0])
                future_1 = executor.submit(generate_packets, slot_index, subnet_list[1]) """
                time.sleep(time_sleep)
                future = executor.submit(generate_packets, slot_index, subnet)
                # Aguarda as tarefas completarem
                """ future_0.result()
                future_1.result() """
                future.result()   
                    
            return 1
    
    def call_submits(self, slot_index, subnet_list, time_sleep):
        for subnet in subnet_list:
            for node in subnet.members:
                node.submit(currtime=slot_index)              
            status = subnet.get_submission_status()
            subnet.notify(status, currtime=slot_index)                     
            subnet.head_node.submit(currtime=slot_index+1)                                                                                
            if status == Status.NODE_COLLISION:
                time.sleep(time_sleep)       
        # Analyse main network collision
        status = self.get_submission_status()
        self.notify(status, currtime=slot_index+1)    
        if status == Status.NODE_COLLISION:
            time.sleep(time_sleep)
        
        return 1
    
    def start_network(self, subnet_list, key, qtd_add, qtd_rem):
        slot_index = 1
        last_generated = 0
        operational_time = 0
        slot_enlace = self.get_slot_enlace()
        package_total = self.get_packates()   
        time_sleep = random.randint(1, 100) / 1000     
        range_generated = random.randint((package_total - 1), (package_total + 1))
        if self.updates:
            print(''''.______    __   __       __    __       ___           _______.    _______   _______     __    __       ___           _______. __    __  
|   _  \  |  | |  |     |  |  |  |     /   \         /       |   |       \ |   ____|   |  |  |  |     /   \         /       ||  |  |  | 
|  |_)  | |  | |  |     |  |__|  |    /  ^  \       |   (----`   |  .--.  ||  |__      |  |__|  |    /  ^  \       |   (----`|  |__|  | 
|   ___/  |  | |  |     |   __   |   /  /_\  \       \   \       |  |  |  ||   __|     |   __   |   /  /_\  \       \   \    |   __   | 
|  |      |  | |  `----.|  |  |  |  /  _____  \  .----)   |      |  '--'  ||  |____    |  |  |  |  /  _____  \  .----)   |   |  |  |  | 
| _|      |__| |_______||__|  |__| /__/     \__\ |_______/       |_______/ |_______|   |__|  |__| /__/     \__\ |_______/    |__|  |__|' ''')
        
        with alive_bar(slot_enlace) as bar:
            while slot_index < slot_enlace:
                # Generate packets                
                while last_generated < range_generated:
                    if key:
                        if (slot_index == (int(range_generated/2))) and key:                                        
                            self.add_member(key=key, qtd=qtd_add, subnet_list=subnet_list, node_index=self.nodes_per_subnet, slot_index=slot_index, time_sleep=time_sleep)
                            operational_time += 1
                            slot_index += 1
                            break       
                        if slot_index == (range_generated - 3) and key: 
                            self.remove_member(subnet_list, qtd_rem, slot_index=slot_index, time_sleep=time_sleep)
                            operational_time += 1
                            slot_index += 1
                            break   
                    operational_time += self.execute_thread(self.generate_packets, slot_index, subnet_list)                      
                    slot_index += self.call_submits(slot_index=slot_index, subnet_list=subnet_list, time_sleep=time_sleep)               
                    last_generated += 1
                    slot_index += 1
                    bar()
                    log_line()
                if key and last_generated == range_generated:
                    if (slot_index == (int(range_generated/2))) and key:                                        
                        self.add_member(key=key, qtd=qtd_add, subnet_list=subnet_list, node_index=self.nodes_per_subnet, slot_index=slot_index, time_sleep=time_sleep)
                    if slot_index == (range_generated - 3) and key: 
                        self.remove_member(subnet_list, qtd_rem, slot_index=slot_index, time_sleep=time_sleep)        
                slot_index += self.call_submits(slot_index=slot_index, subnet_list=subnet_list, time_sleep=time_sleep)    
                operational_time += 1               
                slot_index += 1
                bar()
                log_line()       
        self.clear()
        return operational_time
    
    def add_member(self, key, qtd, subnet_list, node_index, slot_index, time_sleep):
        temp_index = node_index
        self.nodes_per_subnet += qtd
        range = node_index + qtd
        if key:
            if self.updates:
                for subnet in subnet_list:
                    while temp_index < range:
                        #Criação de nós membros com probabilidade de transmissão igual a 1/n (n = número de nós por subrede)
                        node = MemberNode(subnet, temp_index, self.generate_interval, 1/qtd)
                        subnet.members.append(node)
                        node.share_id()
                        temp_index += 1
                    temp_index= node_index
                    print("\n" + " <- "*8 + " NÓS NOVOS ADICIONADOS" + " (QUANTIDADE: " + str(qtd) + ") " + " | " + str(subnet.network_name) + "\n")
                    log_info(subnet, None, Status.CONFIGURATION_NETWORK)
                    log(subnet, None, Status.CONFIGURATION_NETWORK, time=slot_index)
                log_info(self, None, Status.CONFIGURATION_NETWORK)
            else:
                for subnet in subnet_list:
                    while temp_index < range:
                        #Criação de nós membros com probabilidade de transmissão igual a 1/n (n = número de nós por subrede)
                        node = MemberNodeStandard(subnet, temp_index, self.generate_interval, 1/qtd)
                        subnet.members.append(node)
                        temp_index += 1
                    temp_index= node_index
                    print("\n" + " <- "*8 + " NÓS NOVOS ADICIONADOS" + " (QUANTIDADE: " + str(qtd) + ") " + " | " + str(subnet.network_name) + "\n")
                    log_info(subnet, None, Status.CONFIGURATION_NETWORK)
                    log(subnet, None, Status.CONFIGURATION_NETWORK, time=slot_index)
                log_info(self, None, Status.CONFIGURATION_NETWORK)
            log(self, None, Status.CONFIGURATION_NETWORK, time=slot_index)

    
    def remove_member(self, subnet_list, qtd, slot_index, time_sleep):
        node_index = 0
        numero = qtd
        self.nodes_per_subnet -= numero             
        for subnet in subnet_list:
            if self.updates:
                subnet.head_node.id_list = []
            while node_index < numero:
                subnet.members.pop()            
                node_index += 1
            node_index = 0
            if self.updates:
                for node in subnet.members:
                    node.share_id()         
            print("\n" + " -> "*8 + "NÓS REMOVIDOS" +  " (QUANTIDADE: " + str(numero) + ") " + " | " + str(subnet.network_name) + "\n")
            log_info(subnet, None, Status.CONFIGURATION_NETWORK)
            log(subnet, None, Status.CONFIGURATION_NETWORK, time=slot_index)
        log_info(self, None, Status.CONFIGURATION_NETWORK)
        log(self, None, Status.CONFIGURATION_NETWORK, time=slot_index)