#!/usr/bin/env python3
"""
Network Runner CLI
===================
Command-line interface for running a local Gravit Grover network.
"""

import asyncio
import argparse
import logging
from typing import List
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from network.node import NetworkNode, NodeConfig


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Run a local Gravit Grover network'
    )

    parser.add_argument(
        '--nodes',
        type=int,
        default=3,
        help='Number of nodes in the network'
    )

    parser.add_argument(
        '--port-base',
        type=int,
        default=50051,
        help='Base port for nodes (ports will be port-base + node-index)'
    )

    parser.add_argument(
        '--host',
        type=str,
        default='localhost',
        help='Host to bind to'
    )

    parser.add_argument(
        '--storage',
        type=str,
        default='./data',
        help='Storage directory for state'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    return parser.parse_args()


async def run_network(args):
    """Run the network."""
    # Setup
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    # Create nodes
    nodes = []
    for i in range(args.nodes):
        node_id = f"node_{i+1}"
        port = args.port_base + i

        config = NodeConfig(
            node_id=node_id,
            host=args.host,
            port=port,
            storage_path=f"{args.storage}/{node_id}"
        )

        node = NetworkNode(config)
        nodes.append(node)

    try:
        # Start nodes
        logger.info(f"Starting {len(nodes)} nodes...")
        for node in nodes:
            await node.start()

        # Connect all nodes to each other
        logger.info("Connecting nodes...")
        for i, node in enumerate(nodes):
            for j, other in enumerate(nodes):
                if i != j:
                    peer_address = f"{args.host}:{args.port_base + j}"
                    await node.connect_peer(peer_address)

        logger.info("Network running. Press Ctrl+C to stop.")

        # Keep running
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        logger.info("Shutting down network...")
    finally:
        # Stop all nodes
        for node in nodes:
            await node.stop()

        logger.info("Network stopped")


def main():
    """Main entry point."""
    args = parse_args()
    asyncio.run(run_network(args))


if __name__ == '__main__':
    main()
