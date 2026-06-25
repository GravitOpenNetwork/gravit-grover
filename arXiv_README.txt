This is the official repository for the Gravit Grover Network.

The repository contains:

1. README.md - Overview and quick start guide
2. core/ - Implementation of the core algorithms
   - gower/ - Gower Similarity Layer
   - probability/ - Multiplicative Weights
   - consensus/ - Gossip Consensus
   - engine/ - Gravit Grover Engine
3. experiments/ - Jupyter notebooks with POC
4. docs/ - Architecture documentation
5. network/ - P2P implementation

To run the proof-of-concept:
pip install -e .
jupyter notebook experiments/notebooks/01_gower_amplification_poc.ipynb

For the full paper, see docs/whitepaper/gravit_grover.pdf

License: Apache 2.0
