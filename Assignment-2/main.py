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
import heapq
import os
from Tree import Tree

UTX = []       #Unspent Transaction pool
glob_time = 0  # a variable to maintain time used for simulation



def exponential_iterator(mean):
    """
    Generator function that yields exponentially distributed random numbers.

    Args:
        mean (float): Mean of the exponential distribution.

    Yields:
        float: Random numbers drawn from an exponential distribution with the specified mean.
    """
    while True:
        yield np.random.exponential(scale=mean)

class TimedPriorityQueue:
    """
    Priority queue implementation based on timestamps.

    Attributes:
        heap (list): List representing the priority queue.
        counter (int): Counter for maintaining the insertion order of elements.
    """
    def __init__(self):
        """
        Initializes a new TimedPriorityQueue object.
        """
        self.heap = []
        self.counter = 0

    def push(self, variable_list, timestamp):
        """
        Pushes a variable list into the priority queue with a specified timestamp.

        Args:
            variable_list (list): List of variables to be pushed into the queue.
            timestamp (float): Timestamp associated with the variable list.
        """
        heapq.heappush(self.heap, (timestamp, self.counter, variable_list))
        self.counter += 1

    def pop(self):
        """
        Pops the variable list with the smallest timestamp from the priority queue.

        Returns:
            tuple: A tuple containing the timestamp and the variable list.
        """
        ts, _, variable_list = heapq.heappop(self.heap)
        return ts, variable_list

class Transaction:
    """
    Class for creating Transaction details between 2 parties

    Attributes:
        timestamp (float): Time when the transaction was created
        txid (str): Transaction ID
        sender (Peer): Sender of the transaction
        receiver (Peer): Recipitent of transaction
        amount (int): Amount of Bitcoins involved in this transaction
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
        return f'{self.txid}: {self.sender.ID} pays {self.receiver.ID} {self.amount} coins'
    
class Peer:
    def __init__(self, name, id):
        """
        Initializes a new Peer object.

        Args:
            name (str): Name of the peer.
            id (str): Unique identifier for the peer.
        """
        self.simtime = time.time()
        self.name = name
        self.ID = id
        self.is_slow = False
        self.cpuspeed = 1
        self.neighbor = []
        self.lastblkarrivaltime = 0
        self.localchain = Blockchain()
        self.txpool = []
        self.blkqueue = {'00000000000000000000000000000000': self.simtime}
        self.txqueue = {}
        self.balance = 100
        self.blk_itr = None
        self.txn_itr = None
        self.is_mining = False
        self.p = {}     # Dict for Propagation Delay
        self.tot_mining = 0
        self.state0 = False

    def Delay(self, other, msg):
        """
        Calculates the delay in sending a message from this peer to another peer.

        Args:
            other (Peer): The peer to which the message is being sent.
            msg: The message being sent.

        Returns:
            float: The delay in sending the message.
        """
        if other.ID not in self.p.keys():
            self.p[other.ID] = np.random.uniform(10, 500) 
        size = 0
        if isinstance(msg, Transaction):                    # checking type of msg whether it is transaction or block
            size = 8000                                     # size of transaction in bits
        elif isinstance(msg, Block):
            size = 8 * (10 ** 6)                            # size of block in bits
        else:
            # print("Invalid msg type")
            return
        cij = 5 * (10 ** 6)
        if self.is_slow == False and other.is_slow == False:    #checking if both peers are slow or fast
            cij = 100 * (10 ** 6)
        prop = size / cij
        queue_delay = np.random.exponential((96000 / cij), 1)[0]
        delay = self.p[other.ID] + prop + queue_delay           #calculating total delay
        return delay
    
    def sendtx(self, msg : Transaction):
        """
        Sends a transaction message to neighboring peers.

        Args:
            msg (Transaction): The transaction message to be sent.
        """
        for others in self.neighbor:                            #broadcasting to all neighbors
            if msg not in others.txpool:
                t = glob_time + self.Delay(others, msg)         # calculating the delay for transaction
                tpq.push([others, 2, msg], t)

    def sendblock(self, msg : Block, arrv_time):
        """
        Sends a block message to neighboring peers.

        Args:
            msg (Block): The block message to be sent.
            arrv_time (float): Arrival time of the block.
        """
        if ((self.ID == 0 or self.ID == 1) and not msg.miner.ID == self.ID):
            return
        for others in self.neighbor:                            #broadcasting to all neighbors
            if msg not in others.localchain.chain:
                t = arrv_time + self.Delay(others, msg)
                others.blkqueue[msg.blkid] = t                      #updating block queue of other peer and putting timestamp
                tpq.push([others, 6, msg], t)

    def UpdateChain(self, blk : Block, arrival_time):
        """
        Updates the local blockchain with a received block.

        Args:
            blk (Block): The block received.
            arrival_time (float): Arrival time of the block.
        """
        validblk = self.checkValidation(blk)                            #checking if block is valid or not depending on transactions in this block
        if validblk: #We will add the block in the chain if it is a valid block or a fork
            blen = len(self.localchain.longchain)
            if self.localchain.AddBlock(blk,arrival_time):              #check weather it is present in chain or not
                print(f"new block recieved by block by {self.name}")
                self.blkqueue[blk.blkid] = arrival_time                 #updating block queue of this peer and putting timestamp
                self.ballist = self.localchain.blkbal[self.localchain.getLastblk().blkid].copy()                #updating balance list of this peer
                if self.ID not in self.ballist.keys():                  # If peer is not in the dict then he has given the initial bal
                    self.ballist[self.ID] = 100
                self.balance = self.ballist[self.ID]
                tpq.push([self,4,blk],arrival_time)                     #broadcasting block to all neighbors
                self.lastblkarrivaltime = arrival_time
                if not self.is_mining:                                  #if not mining then start mining
                    self.generateblk()
                # if blk.blkid != self.localchain.getLastblk().blkid :    #if block is not a fork then mark transactions as completed
                    print(f'Fork detected at peer ID:{self.ID} for block ID:{blk.blkid}')
                alen = len(self.localchain.longchain)
                if alen == blen:
                    # Long chain not updated, so return
                    return
                # Long chain got updated so check conditions for attacker
                if (self.ID == 0 or self.ID == 1) :
                    # length of private chain
                    temp_height = self.localchain.blkdata[self.localchain.lastplink] + len(self.localchain.private_chain)
                    # length of longest visible change
                    lvc = self.localchain.blkdata[self.localchain.getLastblk().blkid]
                    # print(temp_height-lvc," ",self.ID)
                    if temp_height - lvc > 1:
                        # Lead is greater than 2 and new block added in LVC
                        if self.localchain.AddBlock(self.localchain.private_chain[0],arrival_time):
                            # Add one block from private chain into main chain
                            tpq.push([self,4,self.localchain.private_chain[0]],arrival_time) 
                            self.localchain.lastplink = self.localchain.private_chain[0].blkid
                            self.localchain.private_chain = self.localchain.private_chain[1:]
                    if temp_height - lvc == 1:
                        # Lead of 2 became 1 after adding a block in LVC
                        for privateblk in self.localchain.private_chain:
                            # Broadcast all the blocks in private chain
                            if self.localchain.AddBlock(privateblk,arrival_time):
                                tpq.push([self,4,privateblk],arrival_time) 
                        self.localchain.lastplink = self.localchain.private_chain[-1].blkid
                        self.localchain.private_chain = []
                    if temp_height - lvc == 0:
                        # Lead is one and new block added in LVC State 0'
                        for privateblk in self.localchain.private_chain:
                            # Broadcast all block
                            if self.localchain.AddBlock(privateblk,arrival_time) :
                                tpq.push([self,4,privateblk],arrival_time)
                        # Mine on his block and empty the private chain
                        print("State 0'",self.ID)
                        self.localchain.lastplink = self.localchain.private_chain[-1].blkid
                        self.localchain.private_chain = []
                        # This is state 0' which will go to state 0
                        self.state0 = True
    
                    if temp_height - lvc < 0:
                        # Lead is 0 and new block is added in LVC before attacker
                        # Start the new attack on last block
                        if self.state0:
                            print("State 0' to 0 without attacker block", self.ID)
                        self.state0 = False
                        self.localchain.private_chain = []
                        self.localchain.lastplink = self.localchain.getLastblk().blkid
        return
    

    def UpdateTx(self, tx, arrival_time):
        """
        Updates the peer's transaction pool with a new transaction.

        Args:
            tx (Transaction): The transaction to be added to the pool.
            arrival_time (float): Arrival time of the transaction.
        """
        global UTX
        self.txpool.append(tx)                      # Adding the tx in txpool
        if tx not in UTX:
            UTX.append(tx)                          # Updating the tx in global txpool
        self.sendtx(tx)                             #broadcasting transaction to all neighbors
        return

    def generateTx(self, recv, arrv_time):
        """
        Generates a new transaction and broadcast it to all.

        Args:
            recv (Peer): The recipient peer.
            arrv_time (float): Arrival time of the transaction.
        """
        global UTX
        sender = self
        if self.balance < 1:        # checking bal
            amount = 0
            return
        else:
            amount = random.randint(1,self.balance)
        # amount = 0
        self.balance = self.balance - amount            #updating balance of sender and receiver after transaction
        recv.balance = self.balance + amount
        tx = Transaction(recv,sender,amount)
        print (f"new txn gen by {self.name} at time {glob_time}")
        self.UpdateTx(tx,arrv_time)                     #updating transaction pool of sender and broadcasting transaction to all neighbors
        return


    def checkValidation(self, blk : Block):
        """
        Checks the validity of a received block.

        Args:
            blk (Block): The block to be validated.

        Returns:
            bool: True if the block is valid, False otherwise.
        """
        Txlist = blk.Txlist                             #getting list of transactions in this block
        if blk.plink not in self.localchain.blkdata.keys():
            print('Not a valid block')
            return False
        bal = self.localchain.blkbal[blk.plink].copy()  #getting balance list of all peers from its local longest chain
        for tx in Txlist:
            if tx.sender.ID not in bal.keys():          #checking if sender and receiver are present in balance list or not
                bal[tx.sender.ID] = 100                 #give all peers an initial balance of 100
            if tx.receiver.ID not in bal.keys():
                bal[tx.receiver.ID] = 100
            bal[tx.receiver.ID] = bal[tx.receiver.ID] + tx.amount
            bal[tx.sender.ID] = bal[tx.sender.ID] - tx.amount
            if (bal[tx.sender.ID] < 0 or bal[tx.receiver.ID] < 0):
                print("Invalid Block")
                return False
        return True

    def findvalidTx(self,blktimestamp):
        """
        Finds valid transactions from the global transaction pool.

        Returns:
            list: List of valid transactions.
        """
        global UTX
        txlist = []
        bal = self.localchain.blkbal[self.localchain.getLastblk().blkid].copy()
        for i,tx in enumerate(UTX):                               #itterating through all transactions in UTX and getting the valid txns according to the balance criteria
            if tx.sender.ID not in bal.keys():
                bal[tx.sender.ID] = 100
            if tx.receiver.ID not in bal.keys():
                bal[tx.receiver.ID] = 100
            bal[tx.receiver.ID] = bal[tx.receiver.ID] + tx.amount #updating balance of sender and receiver
            bal[tx.sender.ID] = bal[tx.sender.ID] - tx.amount
            if (bal[tx.sender.ID] < 0 or bal[tx.receiver.ID] < 0):
                bal[tx.receiver.ID] = bal[tx.receiver.ID] - tx.amount
                bal[tx.sender.ID] = bal[tx.sender.ID] + tx.amount
                continue
            if tx.timestamp <= blktimestamp:
                txlist.append(tx)
            if len(txlist) == 999:                                #limiting the number of transactions in a block to 999
                break
        for tx in txlist:
            UTX.remove(tx)
        return txlist

    def marktxcomp(self, Txlist):
        """
        Marks transactions as completed.

        Args:
            Txlist (list): List of transactions to be marked as completed.
        """
        for tx in Txlist:                                         #marking all transactions as completed
            tx.txcomp = True

    def generateblk(self):
        """
        Generates a new block and initiates the mining process.
        """
        if self.ID != 0  and self.ID !=1:
            # Honest Nodes
            newblk = Block([], self, self.localchain.getLastblk().blkid) #creating new block with its parent link as last block in local chain
            newblk.Txlist = self.findvalidTx(newblk.timestamp)
            # print(f'{self.name} started mining...at time {glob_time}')
            k = glob_time + next(self.blk_itr)                           #waiting for time to mine a block
            self.is_mining = True
            tpq.push([self, 5, newblk, []], k)
        else :
            # attacker nodes
            if len(self.localchain.private_chain) != 0:
                # Private chain is not empty so add plink as last blk in private chain
                newblk = Block([], self, self.localchain.private_chain[-1].blkid)             
            else :
                # else add last plink as blk where he wanted to start attack
                newblk = Block([], self, self.localchain.lastplink)
            # newblk.Txlist = []
            k = glob_time + next(self.blk_itr)                           #waiting for time to mine a block
            self.is_mining = True
            tpq.push([self, 7,newblk], k)
           
            
    def add_block_attacker(self,blk : Block):
        """Adding attacker blocks into private chain or broadcasting in state 0

        Args:
            blk (Block): New block to add into private chain
        """
        if self.state0 and blk.plink == self.localchain.lastplink:
            # Attacker is in state 0' and he generated new block so he goes to state 0 by broadcasting newly generated block
            if self.localchain.AddBlock(blk,glob_time):
                self.tot_mining = self.tot_mining + 1
                tpq.push([self,4,blk],glob_time)
                # print("State 0' to 0 with attacker block",self.ID)
                self.state0 = False
                self.localchain.lastplink = blk.blkid
        elif len(self.localchain.private_chain) != 0 or blk.plink == self.localchain.lastplink:
            # If private chain is not empty or new attack and not in state 0'
            self.localchain.private_chain.append(blk)
            self.tot_mining = self.tot_mining + 1
        self.generateblk()
            



    def checkadd(self, newblk: Block, listoftx):
        """
        Checks and adds a new block to the local blockchain if its parent link is still the last block in longest block chain.

        Args:
            newblk (Block): The new block to be added.
            listoftx (list): List of transactions included in the block.
        """
        global UTX
        # # print(f"length of utx is {len(UTX)}")
        # print(f'Checking Block by {self.name} at time {glob_time}')
        if newblk.plink == self.localchain.getLastblk().blkid:          #checking if parent link of this block is still the last block in local chain
            if self.checkValidation(newblk):                            #checking if block is valid or not according to transactions present in it
                
                if self.localchain.AddBlock(newblk,glob_time):          #adding this block to its local chain
                    print(f'genrated id {newblk.blkid}')
                    print(f'Generated Block is Valid Block by {self.name} at time {glob_time}')
                    self.lastblkarrivaltime = newblk.timestamp
                    self.blkqueue[newblk.blkid] = glob_time
                    self.ballist = self.localchain.blkbal[self.localchain.getLastblk().blkid].copy()
                    if self.ID not in self.ballist.keys():
                        self.ballist[self.ID] = 100
                    self.balance = self.ballist[self.ID]
                   
                    self.sendblock(newblk,glob_time)                    #broadcasting newly genarated block to all neighbors
                    # self.tot_mining = self.tot_mining + 1
                    if newblk in self.localchain.longchain:
                        self.marktxcomp(listoftx)                       #marking transactions as completed if block is added to local chain
                    self.is_mining = False                              #mining is completed
            else:
                # print('Generated Block is not Valid Block')
                UTX = UTX + listoftx
        else:
            # print(f'longchain is updated before mining completed at node {self.name}')
            self.is_mining = True                                   #again start mining as local chain is updated and and genarated block is not valid to be added to local chain
            self.generateblk()
            UTX = UTX + listoftx                                    #if block is not added to local chain then add transactions back to UTX
        self.is_mining = False
        
        return


class Network:
    def __init__(self, num, Ttx, Tk, C1, C2):
        """
        Initializes a network of peers.

        Args:
            num (int): Total number of peers in the network.
            Ttx (float): Mean time between transaction generations.
            Tk (float): Mean time between block generation attempts.
            C1 (float): Mining power of the attacker 1.
            C2 (float): Mining power of the attackers 2.
        """
        self.n = num
        self.all_peers = [Peer(f'Node_{i}', i) for i in range(self.n)]
        self.all_peers[0].is_slow = False
        self.all_peers[1].is_slow = False
        self.all_peers[0].cpuspeed = C1 
        self.all_peers[1].cpuspeed = C2  
        # Creates graph
        self.graph = self.createNetwork()
        num_honest = num - 2
        num_slow = num_honest // 2
        num_fast = num_honest - num_slow
        arrz0 = np.array([False] * num_slow + [True] * num_fast)
        np.random.shuffle(arrz0)
        rem_hashing_power = (100-C1-C2)/(num_honest)
        arrz1 = np.array([rem_hashing_power for _ in range(num_honest)])
        for i in range(2, self.n):
            # self.all_peers.append(Peer(f'Node_{i}', i))
            self.all_peers[i].is_slow = arrz0[i-2]
            self.all_peers[i].cpuspeed = arrz1[i-2]      
        k = np.sum(arrz1) + C1 + C2
        for i in range(self.n):
            self.all_peers[i].cpuspeed = self.all_peers[i].cpuspeed/k   
        for i in range(self.n):
            self.all_peers[i].txn_itr = exponential_iterator(Ttx)       #setting mean time between transaction generations
            self.all_peers[i].blk_itr = exponential_iterator(Tk / (self.all_peers[i].cpuspeed))
            # print(Ttx, Tk / (self.all_peers[i].cpuspeed))

    def createNetwork(self):
        """
        Creates a network graph connecting the peers.

        Returns:
            networkx.Graph: The network graph representing peer connections.
        """
        G = nx.Graph()
        G.add_nodes_from(range(self.n))                                     #adding nodes to graph

        num_neighbors_array = [random.randint(3, 6) for _ in range(self.n)] #setting random number between 3-6 of neighbors for each peer
        curr_list = list(range(self.n))                                     #list of all peers which are not satisfied according to its neighbors according to num_neighbors_array

        for node in range(self.n):
            if node not in curr_list:                                       #found exact number of neighbors for this node
                continue
            curr_list.remove(node)

            if len(curr_list) < num_neighbors_array[node]:                  #genrating new list of peers if not enough peers are present in curr_list
                return self.createNetwork()                                 #again start genrating new network

            neighbors = random.sample(curr_list, max(num_neighbors_array[node], 0)) #selecting random neighbors for this node

            for neighbor in neighbors:
                G.add_edge(node, neighbor)                                  #adding edges to graph
                G.add_edge(neighbor, node)                                  #adding edges to graph
                num_neighbors_array[neighbor] -= 1                          #decreasing number of neighbors for this neighbor as it has found this one
                if num_neighbors_array[neighbor] == 0:
                    curr_list.remove(neighbor)                              #removing this neighbor from curr_list  as it has found all its neighbors
            if not curr_list:                                               #if all peers are satisfied with their neighbors then check if it is connected
                break

        while not nx.is_connected(G):                                   # checking the genrated graph is connected or not
            G = self.createNetwork()                                    #if not connected then again start genrating new network
        for node in range(self.n):
            self.all_peers[node].neighbor = [self.all_peers[p] for p in list(G.neighbors(node))]
        for i in range(self.n):
            random_number = random.choice([num for num in range(self.n) if num != i])
            k = self.all_peers[random_number]   
            tpq.push([self.all_peers[i], 1, k], 0)                  #pushing transaction generation event for each peer
        for i in range(self.n):
            tpq.push([self.all_peers[i], 3],0)                     #all peers start mining at time 0

        return G
        
        

    def visualizeNetwork(self):
        """
        visulising network formed by peers and their connections using matplotlib
        """
        nx.draw(self.graph, nx.spring_layout(self.graph), with_labels=True, font_weight='bold')
        plt.savefig("network.png")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Peer2Peer Network')
    parser.add_argument('n', type=int, help='Number of Peers')
    # parser.add_argument('z0', type=float, help='Percent of slow')
    # parser.add_argument('z1', type=float, help='Percent of low CPU') 
    parser.add_argument('Ttx', type=float, help='Mean Time of exponential distribution for Tx')
    parser.add_argument('Tk', type=float, help='Mean Time of exponential distribution for blk')
    parser.add_argument('C1',type=float, help='Mining power of attacker1')
    parser.add_argument('C2',type=float, help='Mining power of attacker2')
    parser.add_argument('N',type=int,help='Number of Blocks to create')
    args = parser.parse_args()
    arg1 = args.n   
    arg2 = args.Ttx
    arg3 = args.Tk
    arg4 = args.C1
    arg5 = args.C2
    N = args.N

    tpq = TimedPriorityQueue()                  #creating a priority queue for maintaining events
    network = Network(arg1,arg2,arg3,arg4,arg5) #creating a network of peers
    network.visualizeNetwork()
    print("Network created")

    #1  ->genrate txn
    #2  ->send txn
    #3  ->genrate blk
    #4  ->send blk
    #5  ->check blockhash with longest chain before addding block
    #6  ->updating block chain of a peer
    #7  ->genrating new block for attacker add_block_attacker



    count = 0                                   #count to stop simulation after genrating required number of blocks 
    while tpq.heap:
        ts, variable_list = tpq.pop()
        if variable_list[1] == 1:
            glob_time = ts
            variable_list[0].generateTx(variable_list[2],glob_time)
            random_number = random.choice([num for num in range(arg1) if num != variable_list[0].ID])
            k=network.all_peers[random_number]
            amount=random.randint(1,100)
            tpq.push([variable_list[0],1,k,amount],glob_time+next(variable_list[0].txn_itr)) #genrating new txn after some time

            # count +=1

        if variable_list[1] == 2:
            glob_time = ts
            variable_list[0].UpdateTx(variable_list[2],glob_time)                            #updating transaction pool of sender and broadcasting transaction to all neighbors
            # count +=1
        
        if variable_list[1] == 3:
            glob_time = ts
            variable_list[0].generateblk() #genrating new block
            count +=1

        if variable_list[1] == 4:
            glob_time =ts
            print(f"broadcasting block by {variable_list[0].name} at {glob_time} of msg {variable_list[2].blkid} to all neighbors")
            variable_list[0].sendblock(variable_list[2],glob_time)                          #checking if it is already sent and broadcasting block to all neighbors

        if variable_list[1] == 5:
            glob_time = ts
            variable_list[0].checkadd(variable_list[2],variable_list[3])                    #checking if block is valid and adding it to local chain and broadcasting it to all neighbors
            count +=1
        
        if variable_list[1] == 6:
            glob_time = ts
            variable_list[0].UpdateChain(variable_list[2],glob_time)                         #updating local chain of a peer and broadcasting block to all neighbors
            print(f"block recieved at {variable_list[0].name} ")
            # count +=1
        if variable_list[1] == 7:
            glob_time = ts
            variable_list[0].add_block_attacker(variable_list[2])

            
        
        if count == N:                                             #stopping simulation after genrating certain no of blocks
            break
    
    while tpq.heap:
        ts, variable_list = tpq.pop()
        if variable_list[1] == 4:
            glob_time =ts
            print(f"broadcasting block by {variable_list[0].name} at {glob_time} of msg {variable_list[2].blkid} to all neighbors")
            variable_list[0].sendblock(variable_list[2],glob_time)  
        if variable_list[1] == 6:
            glob_time = ts
            variable_list[0].UpdateChain(variable_list[2],glob_time)

    # checks if folder exists or not
    if not os.path.exists('Trees'):
        os.makedirs('Trees')
    # writing blockchain into file
    for i in range(network.n):
        tree = Tree(network.all_peers[i].localchain,f'Trees/Node_{i}.txt')
        tree.Print()
    # checks if folder exists or not
    if not os.path.exists('Blockchain_Trees'):
        os.makedirs('Blockchain_Trees')
    # writing blockchain into picture
    for i in range(network.n):                                       #visualizing blockchain of each peer
        network.all_peers[i].localchain.visualize_blockchain(f'Blockchain_Trees/blockchain_{i}')

    # num_attacker_1 = 0
    # tot_attacker_1 = network.all_peers[0].tot_mining                # Total num of blocks mined by attacker 1
    # num_attacker_2 = 0
    # tot_attacker_2 = network.all_peers[1].tot_mining                # Total num of blocks mined by attacker 2
    # for blk in network.all_peers[3].localchain.longchain[1:]:
    #     # Finding number of blocks by attackers in main chain
    #     if blk.miner.ID == 0:
    #         num_attacker_1 = num_attacker_1 + 1
    #     elif blk.miner.ID == 1:
    #         num_attacker_2 = num_attacker_2 + 1
    # num_overall = len(network.all_peers[0].localchain.longchain)
    # tot_overall = len(network.all_peers[0].localchain.chain)
    # print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    # print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    # print("Number of blocks mined by attacker 1 in final public main chain : " + str(num_attacker_1))
    # print("Total number of blocks mined by attacker 1 overall : " + str(tot_attacker_1))
    # print("Number of blocks mined by attacker 2 in final public main chain : " + str(num_attacker_2))
    # print("Total number of blocks mined by attacker 2 overall : " + str(tot_attacker_2))
    # print("Number of block in the final public main chain : " + str(num_overall))
    # print("Total number of blocks generated across all the nodes : " + str(tot_overall))
    # print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    # print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    # print("MPU_node_attacker1 : " + str(num_attacker_1/tot_attacker_1))
    # print("MPU_node_attacker2 : " + str(num_attacker_2/tot_attacker_2))
    # print("MPU_node_overall : " + str(num_overall/tot_overall))
    # print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    # print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")