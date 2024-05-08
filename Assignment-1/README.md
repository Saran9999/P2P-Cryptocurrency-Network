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
python3 main.py num_nodes percent_slownodes percent_lowcpu Txgeneration_meantime Blkgeneration_meantime NumoftimesBlkgeneStart 
```
- num_nodes -> Number of Nodes
- percent_slownodes -> Percentage of slow labeled nodes
- percent_lowcpu -> percntage of Low CPU nodes
- Txgeneration_meantime -> mean time for transaction generation function
- Blkgeneration_meantime -> mean time for BLock generation function
- NumoftimesBlkgeneStart -> Number of times to access the block generation function
#### Example
```
python3 main.py 10 20 20 500 600 100 > out.log
```

## Output
- We will get network.png in same directory as main.py which shows the graph connecting the nodes
- It will create Blockchain_Trees folder in which we have Blockchain tree picture of node i in blockchain_i.png
- It will create Trees folder in which we have Blockchain tree of node i in Node_i.txt
