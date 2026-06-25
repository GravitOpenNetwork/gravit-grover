#!/usr/bin/env python3
"""
Node Runner CLI
===============
Command-line interface for running a single Gravit Grover node.
"""

import asyncio
import argparse
import logging
from typing import Optional
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
        description='Run a Gravit Grover node'
    )

    parser.add_argument(
        '--node-id',
        type=str,
        default='node_1',
        help='Unique node identifier'
    )

    parser.add_argument(
        '--host',
        type=str,
        default='localhost',
        help='Host to bind to'
    )

    parser.add_argument(
        '--port',
        type=int,
        default=50051,
        help='Port to listen on'
    )

    parser.add_argument(
        '--peers',
        type=str,
        nargs='*',
        default=[],
        help='List of peer addresses (host:port)'
    )

    parser.add_argument(
        '--max-peers',
        type=int,
        default=10,
        help='Maximum number of peers'
    )

    parser.add_argument(
        '--storage',
        type=str,
        help='Storage directory for state'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    return parser.parse_args()


async def run_node(args):
    """Run the node."""
    # Setup
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    # Create config
    config = NodeConfig(
        node_id=args.node_id,
        host=args.host,
        port=args.port,
        max_peers=args.max_peers,
        storage_path=args.storage
    )

    # Create node
    node = NetworkNode(config)

    try:
        # Start node
        logger.info(f"Starting node {args.node_id} on {args.host}:{args.port}")
        await node.start()

        # Connect to peers
        if args.peers:
            logger.info(f"Connecting to peers: {args.peers}")
            await node.join_network(args.peers)

        logger.info("Node running. Press Ctrl+C to stop.")

        # Keep running
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        await node.stop()
        logger.info("Node stopped")


def main():
    """Main entry point."""
    args = parse_args()
    asyncio.run(run_node(args))


if __name__ == '__main__':
    main()
