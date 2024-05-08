# P2P-Cryptocurrency-Network
### Team Members
| Roll Number   | Name          |
| ------------- |:-------------:| 
| 210050036     | B.S.S.R.Saran |
| 210050089     | K.Sree Nikhil |
| 210050161     | V.Mahanth Naidu |

## Required Libraries
- numpy
- hashlib
- time
- uuid
  ```
  pip install uuid
  ```
- networkx
  ```
  pip install networkx
  ```
- matplotlib
- heapq
- os
- graphviz
  ```
  sudo apt install graphviz
  ```

## Running Instruction
```
python3 main.py num_nodes Txgeneration_meantime Blkgeneration_meantime C1 C2 NumoftimesBlkgeneStart 
```
- num_nodes -> Number of Nodes
- Txgeneration_meantime -> mean time for transaction generation function
- Blkgeneration_meantime -> mean time for BLock generation function
- C1 -> Hashing power of Attacker 1
- C2 -> Hashing power of Attacker 2
- NumoftimesBlkgeneStart -> Number of times to access the block generation function
#### Example
```
python3 main.py 10 100 600 30 30 100 > out.log
```

## Output
- We will get network.png in same directory as main.py which shows the graph connecting the nodes
- It will create Blockchain_Trees folder in which we have Blockchain tree picture of node i in blockchain_i.png
- It will create Trees folder in which we have Blockchain tree of node i in Node_i.txt

## Referances
- [p2p-blockchain-simulator](https://github.com/km2411/p2p-blockchain-simulator/tree/master)
- [Tree-Printing](https://simonhessner.de/python-3-recursively-print-structured-tree-including-hierarchy-markers-using-depth-first-search/)

