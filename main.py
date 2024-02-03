import argparse
import random
import time
import hashlib
import uuid
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

class Transaction:
    """
    Class for creating Transaction details between 2 parties

    Attributes:
        timestamp (float): Time when the transaction was created
        txid (str): Transaction ID
        sender (str): Sender of the transaction
        receiver (str): Recipitent of transaction
        amount (float): Amount of Bitcoins involved in this transaction
        size (int): Size of Tx in Bytes
        txcomp (bool): Transaction status (complete or not)
    """
    def __init__(self,receiver,sender,amount):
        """Initializes a new Transaction object.

        Args:
            receiver (str): Recipitent of transaction
            sender (str): Sender of the transaction
            amount (float): Amount of Bitcoins involved in this transaction
        """
        # Generating unique Tx ID using timestamp and UUID
        self.timestamp = time.time()
        self.txid = hashlib.md5((str(self.timestamp)+str(uuid.uuid4())).encode()).hexdigest()

        # Details of Tx
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.size = 1000

        #Status of Tx
        self.txcomp = False
    
    def txlog(self):
        """String representing Tx Details

        Returns:
            str: Tx Details in the form TxnID: IDx pays IDy C coins
        """
        return f'{self.txid}: {self.sender} pays {self.receiver} {self.amount} coins'
    
class Block:
    """
    Creating Class for Blocks in BlockChain
    """
    def __init__(self,Txlist,miner,plink = None):
        """
        Initializes a new Block
        max size of block is 1MB

        Args:
            Txlist (List): List of Tx present in Block(Max len 999 because max block size 1MB,empty block size 1KB and Tx size 1KB)
            miner (str): Name of miner who mined this block
            plink (str, optional): Hash of Parent block. Defaults to None.
        """
        # Generating blkid using timestamp and random number b/w 100 and 999
        self.timestamp = time.time()
        self.blkid = hashlib.md5((str(random.randint(100,999))+str(self.timestamp)).encode()).hexdigest()

        # Details of blk
        self.Txlist = Txlist
        self.miner = miner
        self.maxsize = 1e6
        self.plink = plink

class Blockchain:
    def __init__(self,block):
        self.blocklist = [block]

    def addBlock(self,newBlock):
        for block in self.blocklist:
            if newBlock.blkid == block.blkid:
                print('Block is already present in chain')
                return
        newBlock.plink = self.blocklist[-1]
        self.blocklist.append(newBlock)
        return
    
    def printchain(self):
        for b in self.blocklist:
            print(f'Block ID: {b.blkid}')
        return

class Peer:
    def __init__(self,name,id):
        self.name = name
        self.ID = id
        self.is_slow = False
        self.cpuspeed = 1
        self.neighbor = []
        

class Network:
    def __init__(self,num,z0,z1):
        self.n = num
        self.slow = int(z0*self.n/100)
        self.lowcpu = int(z1*self.n/100)
        self.all_peers = np.array([Peer(f'Node_{i}',i) for i in range(self.n)])
        self.graph = self.createNetwork()
        arrz0 = np.array([False for _ in range(self.n)])
        arrz0[:self.slow] = True
        arrz1 = np.array([10 for _ in range(self.n)])
        arrz1[:self.lowcpu] = 1
        np.random.shuffle(arrz0)
        np.random.shuffle(arrz1)
        k = np.sum(arrz1)
        for i in range(self.n):
            self.all_peers[i].is_slow = arrz0[i]
            self.all_peers[i].cpuspeed = arrz1[i]/k
        
        


    def createNetwork(self):
        graph = nx.Graph()
        graph.add_nodes_from(range(self.n))

        for node in range(self.n):
            num_edges = random.randint(3, 6)
            neighbors = random.sample(list(set(range(self.n)) - {node}), num_edges)
            self.all_peers[node] = neighbors
            for neighbor in neighbors:
                graph.add_edge(node, neighbor)
        while not nx.is_connected(graph):
            graph = self.createNetwork()
        
        return graph

    def visualizeNetwork(self):
        nx.draw(self.graph, nx.spring_layout(self.graph), with_labels=True, font_weight='bold')
        plt.show()



if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description='Peer2Peer Network')
    # parser.add_argument('n', type=int, help='Number of Peers')
    # parser.add_argument('z0', type=float, help='Percent of slow')
    # parser.add_argument('z1', type=float, help='Percent of low CPU')
    # parser.add_argument('Tx', type=float, help='Mean Time of exponential distribution')
    # args = parser.parse_args()
    # arg1 = args.n
    # arg2 = args.z0
    network = Network(10,30,30)
    network.visualizeNetwork()