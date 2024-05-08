import random
import time
import hashlib
from collections import deque
# from transaction import Transaction
class Block:
    """
    Creating Class for Blocks in Blockchain
    """

    def __init__(self, Txlist, miner, plink=None):
        """
        Initializes a new Block.

        Args:
            Txlist (List): List of Transactions present in the Block (Max length: 999 because the max block size is 1MB, and each empty block occupies 1KB, and each Transaction size is 1KB).
            miner (Peer): Name of the miner who mined this block.
            plink (str, optional): Hash of the block. Defaults to None.
        """
        # Generating blkid using timestamp and a random number between 100 and 999
        self.timestamp = time.time()
        self.blkid = hashlib.md5((str(random.randint(100, 999)) + str(self.timestamp)).encode()).hexdigest()

        # Details of block
        self.Txlist = Txlist
        self.miner = miner
        self.maxsize = 1e6
        self.plink = plink


class Blockchain:
    """
    Class for managing a blockchain.

    Attributes:
        genesisblk (Block): The genesis block of the blockchain.
        longchain (list): The longest chain in the blockchain.
        chain (list): All blocks in the blockchain.
        blkdata (dict): Mapping of block IDs to block depths.
        blkchild (dict): Mapping of block IDs to their child blocks.
        graph (graphviz.Digraph): Graph representation of the blockchain.
        blktime (dict): Mapping of block IDs to their arrival times.
    """

    def __init__(self):
        """
        Initializes a new blockchain.
        """
        self.genesisblk = Block([], None)
        self.genesisblk.blkid = '00000000000000000000000000000000'
        self.longchain = [self.genesisblk]
        self.chain = [self.genesisblk]
        self.blkdata = {self.genesisblk.blkid: 1}
        self.blkchild = {self.genesisblk.blkid: []}         # It contains child of a node
        self.blktime = {self.genesisblk.blkid: 0}           # Block arrival time list
        self.blkbal = {self.genesisblk.blkid: {}}           # contains bal of all nodes after generation of this block
        self.private_chain = []
        self.lastplink = self.genesisblk.blkid

    def AddBlock(self, newblk, time):
        """
        Adds a new block to the blockchain.

        Args:
            newblk (Block): The new block to be added.
            time (float): The arrival time of the new block.

        Returns:
            bool: True if the block was successfully added, False otherwise.
        """
        if newblk.blkid in self.blkdata.keys():                 # Checking if the block is already present in the chain
            print(f'{newblk.blkid} is already present in chain')
            return False
        pl = newblk.plink                                     # Parent block ID
        if pl in self.blkdata.keys():                       # Checking if the parent block is present in the chain
            self.chain.append(newblk)
            self.blktime[newblk.blkid] = time
            self.blkdata[newblk.blkid] = self.blkdata[pl] + 1   # Adding the new block to the chain
            self.blkchild[pl].append(newblk)                 # Adding the new block as a child of the parent block
            self.blkchild[pl].sort(key=lambda x: self.blktime[x.blkid])  # sorting blocks based on arrival time
            self.blkchild[newblk.blkid] = []
            self.longchain = []
            self.DFS(self.genesisblk)                         # Performing a depth-first search to find the longest chain
            self.getbal(newblk)                               # Finding balance after adding block
            return True
        else:                                                # If the parent block is not present in the chain
            print("Invalid due to plink")
            return False

    def DFS(self, blk):
        """
        Performs a depth-first search to find the longest chain.

        Args:
            blk (Block): The block to start the search from.

        Returns:
            list: The longest chain found.
        """
        if blk is None:
            return []
        max_path = []
        for child in self.blkchild[blk.blkid]:           # For each child of the block
            childpath = self.DFS(child)                  # Perform DFS on the child
            if len(childpath) > len(max_path):           # If the child path is longer than the current max path
                max_path = childpath                     # Update the max path

        self.longchain = max(self.longchain, [blk] + max_path, key=len) # Update the longest chain
        return [blk] + max_path
    
    # def count_nodes_chain(self,id):
    #     count = 0 
    #     for i in range(1,len(self.longchain)):
    #         if((self.longchain)[i].miner.ID == id):
    #             count += 1
    #     return count

    # def count_nodes_total(self,id):
    #     count = 0
    #     queue = deque()
    #     for child in self.blkchild[self.genesisblk.blkid]:
    #         queue.append(child)
    #     while queue:
    #         node = queue.popleft()
    #         if node.miner.ID == id:
    #             count += 1  
    #         for child in self.blkchild[node.blkid]:
    #             queue.append(child)  
    #     return count
        
    # def count_overall_nodes(self):
    #     count = 1
    #     queue = deque()
    #     for child in self.blkchild[self.genesisblk.blkid]:
    #         queue.append(child)
    #     while queue:
    #         node = queue.popleft()
    #         count += 1
    #         for child in self.blkchild[node.blkid]:
    #             queue.append(child)  
    #     return count

    def getbal(self,blk : Block):
        """This will give balance of all node after generating block.
        We will get balance from longest chain

        Args:
            blk (Block): Newly added block

        Returns:
            Dict: This contains Dict mapping from Node ID to balance
        """
        bal = self.blkbal[blk.plink].copy()                                          # Dictionary of balance at Parent Node
        for tx in blk.Txlist:
            if tx.receiver.ID not in bal.keys():        
                bal[tx.receiver.ID] = 100               # giving a intial balance of 100 to all peers
            if tx.sender.ID not in bal.keys():
                bal[tx.sender.ID] = 100
            bal[tx.receiver.ID] = bal[tx.receiver.ID] + tx.amount   # Updating the balances
            bal[tx.sender.ID] = bal[tx.sender.ID] - tx.amount
        if blk.miner.ID not in bal.keys():
            bal[blk.miner.ID] = 100
        bal[blk.miner.ID] = bal[blk.miner.ID] + 50   # Rewarding the miner with 50 coins
        self.blkbal[blk.blkid] = bal
        return bal

    def getLastblk(self):
        """
        Retrieves the last block in the longest chain.

        Returns:
            Block: The last block in the longest chain.
        """
        return self.longchain[-1]

    def printchain(self):
        """
        Prints the blocks in the blockchain.
        """
        for b in self.chain:
            print(f'Block ID: {b.blkid}')
        return

    def visualize_blockchain(self, filename: str):
        """
        Visualizes the blockchain graph.

        Args:
            filename (str): The filename for the visualization image.
        """
        from graphviz import Digraph
        self.graph = Digraph('Blockchain', format='png')    # For Tree diagram of Blockchain
        self.graph.attr(size='10000,10000')
        self.graph.attr(rankdir='LR')    # Left to Right orientation
        for blk in self.chain:
            t = "{:.2f}".format(self.blktime[blk.blkid])
            # Set color based on miner
            node_color = 'black'
            if blk.miner is None:
                node_color = 'blue'  # Genesis block color
            elif blk.miner.ID == 0:
                node_color = 'green'  # Color for miner 0
            elif blk.miner.ID == 1:
                node_color = 'red'  # Color for other miners

            #printing the miner name and arrival time of the block
            if blk.miner is None:
                self.graph.node(blk.blkid, label=f"Miner: Genesis Block\n arr_time: {t}\nBlock Size: {len(blk.Txlist)+1}KB", color=node_color)
            else:
                self.graph.node(blk.blkid, label=f"Miner: {blk.miner.name}\n arr_time: {t}\nBlock Size: {len(blk.Txlist)+1}KB", color=node_color)
            if blk.plink:
                self.graph.edge(blk.plink, blk.blkid)

        self.graph.render(filename, format='png', cleanup=True)