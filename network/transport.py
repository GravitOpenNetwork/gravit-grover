"""
Transport Module
================
Implements network transport layer for Gravit Grover nodes.
"""

import asyncio
import json
import socket
from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass
import grpc
from concurrent import futures

# gRPC imports
try:
    import grpc
    from grpc import aio
except ImportError:
    grpc = None
    aio = None


@dataclass
class TransportConfig:
    """Transport configuration."""
    host: str = "localhost"
    port: int = 50051
    use_grpc: bool = True
    use_websocket: bool = False
    tls_enabled: bool = False
    certificate_path: Optional[str] = None
    max_message_size: int = 1024 * 1024  # 1MB


class TransportLayer:
    """
    Network transport layer.
    """

    def __init__(self, config: TransportConfig):
        self.config = config
        self.handlers = {}
        self.server = None
        self.client = None
        self.connections = {}

    def register_handler(self, message_type: str,
                         handler: Callable[[Dict[str, Any]], None]):
        """
        Register message handler.
        """
        self.handlers[message_type] = handler

    async def start(self):
        """
        Start transport layer.
        """
        if self.config.use_grpc:
            await self._start_grpc()
        else:
            await self._start_tcp()

        print(f"Transport started on {self.config.host}:{self.config.port}")

    async def stop(self):
        """
        Stop transport layer.
        """
        if self.server:
            if self.config.use_grpc:
                await self.server.stop(grace=5)
            else:
                self.server.close()

        print("Transport stopped")

    async def send_message(self, peer: str, message: Dict[str, Any]):
        """
        Send message to peer.
        """
        if self.config.use_grpc:
            await self._send_grpc(peer, message)
        else:
            await self._send_tcp(peer, message)

    async def _start_grpc(self):
        """
        Start gRPC server.
        """
        if grpc is None:
            raise ImportError("grpcio not installed")

        self.server = aio.server(futures.ThreadPoolExecutor(max_workers=10))

        # Define service
        class GravitGroverService:
            async def Gossip(self, request, context):
                message = json.loads(request.message)
                await self._handle_message('grpc', message)
                return GravitGroverResponse(status="ok")

        # Add service to server
        # (In practice, this would be properly defined with protobuf)

        self.server.add_insecure_port(f'{self.config.host}:{self.config.port}')
        await self.server.start()

    async def _start_tcp(self):
        """
        Start TCP server.
        """
        self.server = await asyncio.start_server(
            self._handle_tcp_connection,
            self.config.host,
            self.config.port
        )

    async def _send_grpc(self, peer: str, message: Dict[str, Any]):
        """
        Send message via gRPC.
        """
        # In practice, this would use gRPC client
        pass

    async def _send_tcp(self, peer: str, message: Dict[str, Any]):
        """
        Send message via TCP.
        """
        # In practice, this would send over TCP
        pass

    async def _handle_tcp_connection(self, reader: asyncio.StreamReader,
                                   writer: asyncio.StreamWriter):
        """
        Handle TCP connection.
        """
        try:
            data = await reader.read(self.config.max_message_size)
            message = json.loads(data.decode())
            await self._handle_message('tcp', message)
        except Exception as e:
            print(f"TCP handling error: {e}")
        finally:
            writer.close()
            await writer.wait_closed()

    async def _handle_message(self, transport: str, message: Dict[str, Any]):
        """
        Handle incoming message.
        """
        message_type = message.get('type')
        if message_type in self.handlers:
            await self.handlers[message_type](message)
        else:
            print(f"No handler for message type: {message_type}")

    def get_endpoint(self) -> str:
        """
        Get endpoint address.
        """
        return f"{self.config.host}:{self.config.port}"


class WebSocketTransport(TransportLayer):
    """
    WebSocket transport layer.
    """

    def __init__(self, config: TransportConfig):
        super().__init__(config)
        self.websocket_connections = {}

    async def _start_websocket(self):
        """
        Start WebSocket server.
        """
        # In practice, this would use websockets library
        pass

    async def _send_websocket(self, peer: str, message: Dict[str, Any]):
        """
        Send message via WebSocket.
        """
        if peer in self.websocket_connections:
            ws = self.websocket_connections[peer]
            await ws.send(json.dumps(message))


class TransportFactory:
    """
    Factory for creating transport layers.
    """

    @staticmethod
    def create_transport(config: TransportConfig) -> TransportLayer:
        """
        Create transport layer based on configuration.
        """
        if config.use_websocket:
            return WebSocketTransport(config)
        else:
            return TransportLayer(config)
