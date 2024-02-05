import argparse
import random
import time
import hashlib
import uuid
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from blockchain import Block
from blockchain import Blockchain

UTX = []

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
    
class Peer:
    def __init__(self,name,id):
        self.simtime = time.time()
        self.name = name
        self.ID = id
        self.is_slow = False
        self.cpuspeed = 1
        self.neighbor = []
        self.lastblkarrivaltime = time.time()
        self.localchain = Blockchain(self.genesisblk)
        self.txpool = []
        self.blkqueue = {'00000000000000000000000000000000': self.simtime}
        self.txqueue = {}
        self.balance = 100

    def Delay(self,other,msg):
        size = 0
        if isinstance(msg,Transaction):
            size = 8000
        elif isinstance(msg,Block):
            size = 8*(10**6)
        else:
            print("Invalid msg type")
            return
        pij = np.random.uniform(10,500)/1000
        cij = 5*(10**6)
        if self.is_slow == False and other.is_slow == False:
            cij = 100*(10**6)
        prop = size/cij
        queue_delay = np.random.exponential((size/cij),1)[0]
        delay = pij+prop+queue_delay
        return delay
    
    def sendtx(self,msg,delay):
        for others in self.neighbor:
            if msg not in others.txpool:
                others.txpool.append(msg)
                t = delay+self.Delay(others,msg)
                others.txqueue[msg.txid] = t
                others.sendtx(msg,t)

    def sendblock(self,msg,delay):
        for others in self.neighbor:
            if msg not in others.localchain.chain:
                t = delay+self.Delay(others,msg)
                others.blkqueue[msg.blkid] = t
                is_fork = self.forkhandler(msg,t)
                if not is_fork:
                    others.UpdateChain(msg,t)
                    others.sendblock(msg,t)
        return

    def forkhandler(self,msg,arrival_time):
        if msg.plink == self.localchain.getLastblk().plink and msg.blkid != self.localchain.getLastblk().blkid:
            print(f'Fork Detected at peer {self.name}')
            if arrival_time > self.lastblkarrivaltime:
                self.lastblkarrivaltime = arrival_time
                self.localchain.AddBlock(msg)
                self.sendblock(msg,arrival_time) 
                return True
            else:
                self.localchain.longchain = self.localchain.longchain[:-1]
                self.localchain.AddBlock(msg)
                self.sendblock(msg,arrival_time)
        return False

    def UpdateChain(self,blk,arrival_time):
        if blk.blkid in self.localchain.blkdata.keys():
            print("No need to update chain because it is already present in chain")
            return
        self.localchain.AddBlock(blk)
        self.lastblkarrivaltime = arrival_time
        return
    
    def generateTx(self,sender,amount):
        recv = self
        if self.balance < 1:
            print("Insufficent funds")
            return
        tx = Transaction(recv,sender,amount)
        self.txpool.append(tx,tx.timestamp)
        UTX.append(tx)
        self.sendtx()
        return

    def generateblk(self):
        pass



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
        G = nx.Graph()
        G.add_nodes_from(range(self.n))

        num_neighbors_array = [random.randint(3,6) for _ in range(self.n)]
        curr_list = list(range(self.n))

        for node in range(self.n):
            if node not in curr_list:
                continue
            curr_list.remove(node)
            
            if len(curr_list) < num_neighbors_array[node]:
                return self.createNetwork()
            
            neighbors = random.sample(curr_list, max(num_neighbors_array[node], 0))
            
            for neighbor in neighbors:
                G.add_edge(node, neighbor)
                G.add_edge(neighbor, node)            
                num_neighbors_array[neighbor] -= 1            
                if num_neighbors_array[neighbor] == 0:
                    curr_list.remove(neighbor)
            if not curr_list:
                break

        while not nx.is_connected(G):
            G = self.createNetwork()
        for node in range(self.n):
            self.all_peers[node] = [self.all_peers[p] for p in list(G.neighbors(node))]
        return G

    def visualizeNetwork(self):
        nx.draw(self.graph, nx.spring_layout(self.graph), with_labels=True, font_weight='bold')
        plt.show()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Peer2Peer Network')
    parser.add_argument('n', type=int, help='Number of Peers')
    parser.add_argument('z0', type=float, help='Percent of slow')
    parser.add_argument('z1', type=float, help='Percent of low CPU')
    parser.add_argument('Tx', type=float, help='Mean Time of exponential distribution')
    args = parser.parse_args()
    arg1 = args.n
    arg2 = args.z0
    network = Network(10,30,30)
    network.visualizeNetwork()