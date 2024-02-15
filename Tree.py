from blockchain import Block
from blockchain import Blockchain

class Tree:
    """
    Class to print blockchain tree in files
    """
    def __init__(self,blkchain: Blockchain,filename: str):
        """
        Initializes a new tree

        Args:
            blkchain (Blockchain): Block chain we want to print in file
            filename (str): Filename
        """
        self.n = len(blkchain.chain)
        self.blkchain = blkchain
        self.root = self.blkchain.genesisblk
        self.filename = filename
    
    def Print(self):
        """
        Function to print blockchain in file
        """
        with open(self.filename, "w") as file:
            self.PrintTree(self.root,file)
    
    def PrintTree(self, blk: Block,file, markerStr="+- ", levelMarkers=[]):
        """
        Recursive function to print tree
        Ref : https://simonhessner.de/python-3-recursively-print-structured-tree-including-hierarchy-markers-using-depth-first-search/

        Args:
            blk (Block): Block we are currently printing
            file (File): File discriptor
            markerStr (str, optional): To differ the new nodes. Defaults to "+- ".
            levelMarkers (list, optional): level of tabs. Defaults to [].
        """
        emptyStr = " "*len(markerStr)
        connectionStr = "|" + emptyStr[:-1]
        level = len(levelMarkers)
        mapper = lambda draw: connectionStr if draw else emptyStr
        # Joining required amount of tabs
        markers = "".join(map(mapper, levelMarkers[:-1]))
        markers += markerStr if level > 0 else ""
        # Printing block data
        file.write(f"{markers}Block ID: {blk.blkid}\n")
        if blk.miner is None:
            file.write(f"{markers}|__ Miner: Genesis Block\n")
        else:
            file.write(f"{markers}|__ Miner: {blk.miner.name}\n")
        file.write(f"{markers}|__ Size: {len(blk.Txlist)+1}KB\n")
        # Going to child
        for i, child in enumerate(self.blkchain.blkchild[blk.blkid]):
            isLast = i == len(self.blkchain.blkchild[blk.blkid]) - 1
            self.PrintTree(child,file, markerStr, [*levelMarkers, not isLast])
