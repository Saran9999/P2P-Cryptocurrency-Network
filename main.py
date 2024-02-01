import argparse
import random
import time
import hashlib
import uuid

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
    
    def __txlog__(self):
        """String representing Tx Details

        Returns:
            str: Tx Details in the form TxnID: IDx pays IDy C coins
        """
        return f'{self.txid}: {self.sender} pays {self.receiver} {self.amount} coins'
    
class Block:
    """
    Creating Class for Blocks in BlockChain
    """
    def __init__(self,Txlist,miner,mine_time,index,plink = None):
        """
        Initializes a new Block
        max size of block is 1MB

        Args:
            Txlist (List): List of Tx present in Block(Max len 999 because max block size 1MB,empty block size 1KB and Tx size 1KB)
            miner (str): Name of miner who mined this block
            mine_time (float): Time when the this block was successfully mined
            index (int): index of block
            plink (str, optional): Hash of Parent block. Defaults to None.
        """
        # Generating blkid using timestamp and random number b/w 100 and 999
        self.timestamp = time.time()
        self.blkid = hashlib.md5((str(random.randint(100,999))+str(self.timestamp)).encode()).hexdigest()

        # Details of blk
        self.Txlist = Txlist
        self.miner = miner
        self.mine_time = mine_time
        self.index = index
        self.maxsize = 1e6
        self.plink = plink
    
    def __id__(self):
        """Returns blkid of a block

        Returns:
            str: Block ID of a block
        """
        return str(self.blkid)

class Blockchain:
    def __init__(self,blk):
        self.blklist = [blk]

    # def Addblk(self,newblk):
    #     for blk in self.blklist:

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Peer2Peer Network')
    parser.add_argument('n', type=int, help='Number of Peers')
    parser.add_argument('z0', type=float, help='Percent of slow')
    parser.add_argument('z1', type=float, help='Percent of low CPU')
    parser.add_argument('Tx', type=float, help='Mean Time of exponential distribution')
    args = parser.parse_args()
    arg1 = args.n
    arg2 = args.z0