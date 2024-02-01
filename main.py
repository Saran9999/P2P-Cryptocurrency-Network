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

        #Status of Tx
        self.txcomp = False
    
    def __txlog__(self):
        """String representing Tx Details

        Returns:
            str: Tx Details in the form TxnID: IDx pays IDy C coins
        """
        return f'{self.txid}: {self.sender} pays {self.receiver} {self.amount} coins'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Peer2Peer Network')
    parser.add_argument('n', type=int, help='Number of Peers')
    parser.add_argument('z0', type=float, help='Percent of slow')
    parser.add_argument('z1', type=float, help='Percent of low CPU')
    parser.add_argument('Tx', type=float, help='Mean Time of exponential distribution')
    args = parser.parse_args()
    arg1 = args.n
    arg2 = args.z0