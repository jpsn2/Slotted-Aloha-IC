#!/usr/bin/env python3
from tkinter import*
from aloha.aloha import Aloha
import fire

def main(*args, **kwargs):
    # Hierarchical Slotted Aloha
    hs_aloha = {
        "subnets": 2,
        "nodes_per_subnet": 4,
        "generate_interval": 1, # delay
        "head_node_generate": False,
        "head_node_coin": True, # Girar moeda significa escolher se o pacote será enviado ou não
        # "member_node_coin": False, # Criei agora, daqui a pouco a gente arruma no código
        "max_loop": 500, # Número de geração de Pacotes
        "key": False, # Chave para criar e remover nós na rede durante a execução
        "qtd_add": 2, #Quantidade de nós novos
        "qtd_rem": 1, #Quantidade de nós removidos
        "updates": True, #Defini se o protocolo irá funcionar com as melhorias
    }

    final = {
        **hs_aloha,
        **kwargs
    }

    (Aloha(**final).create().start().analyse())
    #(Aloha(**final).generate_packets(0))

if __name__ == "__main__":
    fire.Fire(main)