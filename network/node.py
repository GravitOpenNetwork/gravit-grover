"""
Node Module
===========
Implements Gravit Grover network node.
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
import numpy as np

from core.engine.grover_engine import GroverEngine
from core.consensus.gossip import GossipProtocol
from core.consensus.mixing import MixingMatrix
from core.consensus.security import SignatureManager, IdentityVerifier, SecureMessageHandler


@dataclass
class NodeConfig:
    """Configuration for network node."""
    node_id: str
    host: str = "localhost"
    port: int = 50051
    max_peers: int = 10
    heartbeat_interval: float = 5.0
    gossip_interval: float = 1.0
    consensus_timeout: float = 30.0
    storage_path: Optional[str] = None


class NetworkNode:
    """
    Gravit Grover network node.
    """

    def __init__(self, config: NodeConfig):
        self.config = config
        self.node_id = config.node_id

        # Core components
        self.engine = GroverEngine()
        self.gossip = GossipProtocol(config.node_id)
        self.mixing = MixingMatrix()

        # Security components
        self.signature_manager = SignatureManager()
        self.identity_verifier = IdentityVerifier()
        self.secure_handler = SecureMessageHandler(
            config.node_id,
            self.signature_manager,
            self.identity_verifier
        )

        # State
        self.peers: Set[str] = set()
        self.state_version = 0
        self.running = False
        self.tasks: List[asyncio.Task] = []

        # Statistics
        self.message_count = 0
        self.consensus_rounds = 0
        self.start_time = time.time()

    async def start(self):
        """
        Start the node.
        """
        self.running = True

        # Generate keypair
        self.signature_manager.generate_keypair()

        # Register identity
        self.identity_verifier.register_identity(
            self.node_id,
            {'node_id': self.node_id}
        )

        # Start components
        await self.gossip.start()

        # Start tasks
        self.tasks.append(asyncio.create_task(self._consensus_loop()))
        self.tasks.append(asyncio.create_task(self._health_check_loop()))

        print(f"Node {self.node_id} started on {self.config.host}:{self.config.port}")

    async def stop(self):
        """
        Stop the node.
        """
        self.running = False

        # Stop components
        await self.gossip.stop()

        # Cancel tasks
        for task in self.tasks:
            task.cancel()

        await asyncio.gather(*self.tasks, return_exceptions=True)

        print(f"Node {self.node_id} stopped")

    async def join_network(self, boot_peers: List[str]):
        """
        Join the network using boot peers.
        """
        for peer in boot_peers:
            await self.connect_peer(peer)

    async def connect_peer(self, peer_address: str):
        """
        Connect to a peer.
        """
        # In practice, this would establish actual connection
        peer_id = f"peer_{len(self.peers)}"
        self.peers.add(peer_id)
        self.gossip.add_peer(peer_id)

        print(f"Node {self.node_id} connected to {peer_id}")

    async def propose_hypothesis(self, hypothesis: Dict[str, Any]):
        """
        Propose a new hypothesis.
        """
        # Add to engine
        self.engine.add_hypothesis(hypothesis)

        # Broadcast to peers
        message = self.secure_handler.create_secure_message({
            'type': 'proposal',
            'hypothesis': hypothesis
        })
        await self._broadcast_message(message)

        print(f"Node {self.node_id} proposed hypothesis: {hypothesis}")

    async def _consensus_loop(self):
        """
        Main consensus loop.
        """
        while self.running:
            try:
                await asyncio.sleep(self.config.gossip_interval)

                # Run one consensus step
                self.engine.step()
                self.consensus_rounds += 1

                # Get consensus state
                state = self.engine.get_state()

                # Update gossip state
                self.gossip.update_state('consensus', state)

                # Check convergence
                if self.engine.is_converged():
                    await self._handle_convergence()

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Consensus loop error: {e}")

    async def _health_check_loop(self):
        """
        Health check loop.
        """
        while self.running:
            try:
                await asyncio.sleep(self.config.heartbeat_interval)

                # Send heartbeat
                heartbeat = self.secure_handler.create_secure_message({
                    'type': 'heartbeat',
                    'state': self.get_state()
                })
                await self._broadcast_message(heartbeat)

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Health check error: {e}")

    async def _handle_convergence(self):
        """
        Handle convergence event.
        """
        best_hypothesis = self.engine.get_best_hypothesis()
        print(f"Convergence achieved: {best_hypothesis}")

        # Broadcast convergence
        message = self.secure_handler.create_secure_message({
            'type': 'convergence',
            'best_hypothesis': best_hypothesis
        })
        await self._broadcast_message(message)

    async def _broadcast_message(self, message: Dict[str, Any]):
        """
        Broadcast message to all peers.
        """
        for peer in self.peers:
            await self._send_to_peer(peer, message)

        self.message_count += 1

    async def _send_to_peer(self, peer: str, message: Dict[str, Any]):
        """
        Send message to specific peer.
        """
        # In practice, this would send over the network
        # For simulation, we handle locally
        await self._handle_message(peer, message)

    async def _handle_message(self, sender: str, message: Dict[str, Any]):
        """
        Handle incoming message.
        """
        # Verify message
        valid, reason = self.secure_handler.verify_secure_message(message)
        if not valid:
            print(f"Invalid message from {sender}: {reason}")
            return

        # Process message
        payload = message.get('payload', {})
        msg_type = payload.get('type')

        if msg_type == 'proposal':
            await self._handle_proposal(sender, payload)
        elif msg_type == 'heartbeat':
            await self._handle_heartbeat(sender, payload)
        elif msg_type == 'convergence':
            await self._handle_convergence_message(sender, payload)

    async def _handle_proposal(self, sender: str, payload: Dict[str, Any]):
        """
        Handle hypothesis proposal.
        """
        hypothesis = payload.get('hypothesis')
        if hypothesis:
            self.engine.add_hypothesis(hypothesis)
            print(f"Node {self.node_id} received proposal from {sender}")

    async def _handle_heartbeat(self, sender: str, payload: Dict[str, Any]):
        """
        Handle heartbeat message.
        """
        state = payload.get('state', {})
        print(f"Node {self.node_id} received heartbeat from {sender}")

    async def _handle_convergence_message(self, sender: str, payload: Dict[str, Any]):
        """
        Handle convergence message.
        """
        best_hypothesis = payload.get('best_hypothesis')
        print(f"Node {self.node_id} received convergence from {sender}: {best_hypothesis}")

    def get_state(self) -> Dict[str, Any]:
        """
        Get node state.
        """
        return {
            'node_id': self.node_id,
            'state_version': self.state_version,
            'peers': len(self.peers),
            'message_count': self.message_count,
            'consensus_rounds': self.consensus_rounds,
            'uptime': time.time() - self.start_time
        }

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get node statistics.
        """
        return {
            'node_id': self.node_id,
            'peers': len(self.peers),
            'state_version': self.state_version,
            'message_count': self.message_count,
            'consensus_rounds': self.consensus_rounds,
            'uptime': time.time() - self.start_time,
            'gossip_stats': self.gossip.get_statistics()
        }
