# CDC-Scoreboard-6600

Given 2 input files, config.txt and inst.txt.
The scoreboard is configured as per the specifications in the config.txt file

How to read the input files.

* Config.txt:
    each line contains the functional unit, number of units and the latency for the execution phase.
    
* Inst.txt:
    This file contains the instruction set, in assembly language. 
    
The python program (code.py) reads the two input files, and simulates the 5 stages for each instruction [Fetch, Issue, Read, Execute, Write Back].

The code simulates this process for each instruction and determines the clock cycle of the completion of each stage for every instruction.

The simulator checks for 'Read after Write Hazards', 'Write after Write Hazards', 'Structural Hazards', 'Instruction-Cache hits', 'Data-cache hits' and 'Data-cache with dirty blocks'

The code generates an output file 'results.txt' which contains the clock cycle number for each stage, for every instruction.

*** Missing concepts ***

- Memory Bus conflict. When the Memory Bus is busy fetching data into the D-cache and an I-cache miss occurs, data fetch into I-cache is not stalled appropriately.
- Cache hit counts are not correctly displayed. 
