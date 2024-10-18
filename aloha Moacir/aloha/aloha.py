import time
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import pandas as pd
from aloha.network import Network
from aloha_standard.member_node import MemberNodeStandard
from aloha_standard.head_node import HeadNodeStandard
from alive_progress import alive_bar
from aloha.head_node import HeadNode
from aloha.member_node import MemberNode
from aloha.aloha_logging import Status, init_log, log_info, log, custom_log
import random
class Aloha:
    def __init__(
        self,
        subnets: int,
        nodes_per_subnet: int,
        max_loop: int,
        generate_interval: int,
        head_node_generate: bool,
        head_node_coin: bool,
        key: bool,
        qtd_add: int,
        qtd_rem: int,
        updates: bool,
        time_sleep: int = 5,  
    ):
        self.generate_interval = generate_interval
        self.nodes_per_subnet = nodes_per_subnet
        self.subnets = subnets
        self.loops = nodes_per_subnet + max_loop
        self.head_node_generate = head_node_generate
        self.head_node_coin = head_node_coin
        self.time_sleep = time_sleep
        self.operational_time = 0
        #self.slot_range = self.nodes_per_subnet * 3 * (self.generate_interval ** 2) + 1
        self.slot_range = self.loops * self.generate_interval + 1 + self.nodes_per_subnet
        self.key = key
        self.qtd_add = qtd_add
        self.updates = updates
        self.qtd_rem = qtd_rem
        
        self.subnet_list = []

    def create(self):
        """
        Create network structure
        """
        init_log()
        self.main_network = Network("BASE_STATION", self.nodes_per_subnet, self.generate_interval, self.loops, self.head_node_generate, self.updates)
        self.main_network.set_slot_enlace(self.slot_range)
        self.subnet_list = []
        
        for i in range(self.subnets):
            subnet = Network(f"SUBNET_{i}", self.nodes_per_subnet, self.generate_interval, self.loops, self.head_node_generate, self.updates) # Network é a Subnet
            subnet.set_slot_enlace(self.slot_range)
            if self.updates:
                head_node = HeadNode(self.main_network, subnet,
                                        self.head_node_coin, 1.0/self.subnets)
            else:
                head_node = HeadNodeStandard(self.main_network, subnet,
                                        self.head_node_coin, 1.0/self.subnets)
            subnet.head_node = head_node
            self.main_network.members.append(head_node)

            for node_index in range(self.nodes_per_subnet):
                #Criação de nós membros com probabilidade de transmissão igual a 1/n (n = número de nós por subrede)
                if self.updates:
                    node = MemberNode(subnet, node_index, self.generate_interval, 1/self.nodes_per_subnet)
                    subnet.members.append(node)
                    node.share_id()
                else:
                    node = MemberNodeStandard(subnet, node_index, self.generate_interval, 1/self.nodes_per_subnet)
                    subnet.members.append(node) 

            self.subnet_list.append(subnet)
            
            if self.updates:
                head_node.share_id()
            #log_info(subnet, None, Status.CONFIGURATION_NETWORK)
            log(subnet, (head_node.name + " | " + str(i)), Status.CONFIGURATION_NETWORK, time=0)

        if self.generate_interval < 0:
            self.generate_packets(0)
        
        self.operational_time += 1
        #log_info(self.main_network, None, Status.CONFIGURATION_NETWORK)
        log(self.main_network, None, Status.CONFIGURATION_NETWORK, time=0)
        
        return self

    def start(self):
        """
        Run aloha simulation
        """
        # Geração de semente aleatória para o tempo de envio
        self.seed = random.randint(1, 100)
        np.random.seed(self.seed)
         
        # Salva valor de semente nos logs
        custom_log(f"SEED: {self.seed}")
        
        packets_per_subnet = self.nodes_per_subnet
        if self.head_node_generate:
            packets_per_subnet += 1
            
        self.operational_time += self.main_network.start_network(self.subnet_list, self.key, self.qtd_add, self.qtd_rem)
        
        return self

    def analyse(self):
        columns = ["timestamp", "network", "node", "type", "message", "time"]
        log_df = pd.read_csv("data/aloha.log", skiprows=None, header=None)
        log_df.columns = columns
        log_df["type"] = log_df["type"].str.strip()

        has_debug = log_df["timestamp"].str.contains("DEBUG:root")
        log_df = log_df[has_debug].copy()

        log_df["timestamp"] = log_df["timestamp"].apply(
            lambda t: t.split("DEBUG:root:").pop()
        )
        log_df["timestamp"] = pd.to_datetime(log_df["timestamp"])

        log_df.to_csv("data/log.csv", index=False)

        print(f"Estatísticas gerais: (SEMENTE: {self.seed})")
        df = (
            log_df.groupby(["network", "type"], as_index=False)
            .agg({"timestamp": "count"})
            .pivot(index="network", columns="type", values="timestamp")
            .fillna(0)
        )
        
        if "IDLE" not in df.columns:
            df["IDLE"] = 0
        else:
            df["IDLE"] = (df["IDLE"] * 100) / (self.operational_time + self.nodes_per_subnet)

        if "SUCCESS" not in df.columns:
            df["SUCCESS"] = 0
        else:
            df["SUCCESS"] = (df["SUCCESS"] * 100) / (self.operational_time + self.nodes_per_subnet)

        if "PARTIAL_NODE_COLISION" not in df.columns:
            df["PARTIAL_NODE_COLISION"] = 0
        else:
            df["PARTIAL_NODE_COLISION"] = (df["PARTIAL_NODE_COLISION"] * 100) / (self.operational_time + self.nodes_per_subnet)

        if "NODE_COLLISION" not in df.columns:
            df["NODE_COLLISION"] = 0
        else:
            df["NODE_COLLISION"] = (df["NODE_COLLISION"] * 100) / (self.operational_time + self.nodes_per_subnet)

        if "CONFIGURATION_NETWORK" not in df.columns:
            df["CONFIGURATION_NETWORK"] = 0
        else:
            df["CONFIGURATION_NETWORK"] = ((df["CONFIGURATION_NETWORK"] + self.nodes_per_subnet) * 100) / (self.operational_time + self.nodes_per_subnet)
        
        if "GENERATING_PACKAGES" not in df.columns:
            df["GENERATING_PACKAGES"] = 0

        if "COLLISION" not in df.columns:
            df["COLLISION"] = df["PARTIAL_NODE_COLISION"] + \
                df["NODE_COLLISION"]      
      
        """ df["BUSY"] = df["COLLISION"]+ df["SUCCESS"] + df["CONFIGURATION_NETWORK"]     
        df["THROUGHPUT"] = (df["SUCCESS"] / (df["IDLE"] + df["BUSY"])) * 100 """

        print(df)
        df.to_csv("data/metrics.csv")