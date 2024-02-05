import random
import time
import hashlib

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
    def __init__(self):
        self.genesisblk = Block([],None)
        self.genesisblk.blkid = '00000000000000000000000000000000'
        self.longchain = [self.genesisblk]
        self.chain = [self.genesisblk]
        self.blkdata = {self.genesisblk.blkid: 0}

    def AddBlock(self,newblk):
        if newblk.blkid in self.blkdata.keys():
            print(f'{newblk.blkid} is already present in chain')
            return False
        if newblk.plink is None:
            newblk.plink = self.chain[-1].blkid
            self.chain.append(newblk)
            self.longchain.append(newblk)
            self.blkdata[newblk.blkid] = newblk.timestamp
            return True
        else:
            plink = newblk.plink
            blk = newblk
            level = 0
            while(blk.blkid != '00000000000000000000000000000000'):
                if plink == None:
                    return False
                if plink not in self.blkdata:
                    print("Not a Valid Block")
                    return False
                for b in self.chain:
                    if plink == b.blkid:
                        if b in self.longchain:
                            self.chain.append(newblk)
                            self.blkdata[newblk.blkid] = self.blkdata[b.blkid]+level+1
                            if self.blkdata[newblk.blkid] == len(self.longchain):
                                self.longchain.append(newblk)
                            return True
                        blk = b
                        plink = blk.plink
                        level = level + 1
                        break
            self.chain.append(newblk)
            self.blkdata[newblk.blkid] = 1
            if self.blkdata[newblk.blkid] == len(self.longchain):
                self.longchain.append(newblk)
            return True

    def getLastblk(self):
        return self.longchain[-1]

    def printchain(self):
        for b in self.chain:
            print(f'Block ID: {b.blkid}')
        return