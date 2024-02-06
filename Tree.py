from blockchain import Block
from blockchain import Blockchain

# Ref: https://simonhessner.de/python-3-recursively-print-structured-tree-including-hierarchy-markers-using-depth-first-search/
class Node:
    def __init__(self,blk: Block):
        self.data = blk
        self.child = []

class Tree:
    def __init__(self,blkchain: Blockchain,filename: str):
        self.n = len(blkchain.chain)
        self.blkchain = blkchain
        self.blklist = {}
        self.root = self.blkchain.genesisblk
        self.filename = filename

    def GenerateTree(self):
        for blk in self.blkchain.chain:
            self.blklist[blk.blkid] = []
        for blk in self.blkchain.chain:
            if blk.plink is not None:
                self.blklist[blk.plink].append(blk)
    
    def Print(self):
        self.PrintTree(self.root)
    
    def PrintTree(self, blk: Block, markerStr="+- ", levelMarkers=[]):
        emptyStr = " "*len(markerStr)
        connectionStr = "|" + emptyStr[:-1]
        level = len(levelMarkers)
        mapper = lambda draw: connectionStr if draw else emptyStr
        markers = "".join(map(mapper, levelMarkers[:-1]))
        markers += markerStr if level > 0 else ""
        file = open(self.filename,"a")
        file.write(f"{markers}{blk.blkid}\n")
        file.close()
        for i, child in enumerate(self.blklist[blk.blkid]):
            isLast = i == len(self.blklist[blk.blkid]) - 1
            self.PrintTree(child, markerStr, [*levelMarkers, not isLast])
