# Gravit Grover Protocol Specification

## Overview

The Gravit Grover Network (GGN) uses a peer-to-peer protocol for distributed hypothesis evaluation and consensus formation. This document specifies the wire protocol, message formats, and communication patterns.

## Transport Layer

### gRPC Configuration

```protobuf
syntax = "proto3";

package gravitgrover;

service GravitGrover {
    rpc Gossip (GossipRequest) returns (GossipResponse);
    rpc QueryState (QueryRequest) returns (QueryResponse);
    rpc ProposeHypothesis (ProposalRequest) returns (ProposalResponse);
    rpc SyncState (SyncRequest) returns (SyncResponse);
}
```

### Message Formats

#### GossipMessage

```protobuf
message GossipMessage {
    string node_id = 1;
    int64 timestamp = 2;
    repeated HypothesisEntry hypotheses = 3;
    bytes signature = 4;
    int32 sequence_number = 5;
}

message HypothesisEntry {
    string id = 1;
    string content = 2;
    float weight = 3;
    float consistency_score = 4;
    int64 timestamp = 5;
}
```

#### State Message
```protobuf
message StateMessage {
    string node_id = 1;
    int64 version = 2;
    repeated HypothesisEntry hypotheses = 3;
    bytes hash = 4;
    bytes signature = 5;
}
```

## Protocol Flow

### 1. Node Discovery

Nodes discover peers through:

* Static Configuration: Manual peer list
* Dynamic Discovery: Multicast DNS or DHT
* Bootstrapping: Hardcoded seed nodes

### 2. Gossip Propagation

Push-Pull Algorithm:
1. Node selects random peer
2. Node sends push message with state
3. Peer responds with push message
4. Both update state and resolve conflicts
3. Consensus Round

### Consensus Round Protocol:

1. Nodes generate local hypotheses
2. Gower similarity computed
3. Multiplicative weights update
4. Grover amplification applied
5. Gossip consensus achieved

## Wire Protocol Details

### Message Headers

Header Format:
- Magic Number: 0x47564752 (GVR)
- Version: uint8
- Message Type: uint8
- Message Length: uint32
- Timestamp: int64
- Node ID: bytes(32)
- Checksum: bytes(32)

### Message Types

| Type | Value | Description |
| --- | --- | --- |
| GOSSIP | 0x01 | Gossip state exchange |
| STATE_SYNC | 0x02 | Full state synchronization |
| PROPOSAL | 0x03 | Hypothesis proposal |
| RESPONSE | 0x04 | Response to query |
| VOTE | 0x05 | Consistency vote |
| HEARTBEAT | 0x06 | Health check |

## Security Protocol

### Message Signing

All messages are signed using Ed25519:

```text
signature = Ed25519.sign(private_key, message_bytes)
```

### Message Verification
```text
is_valid(message, signature, public_key):
    return Ed25519.verify(public_key, message, signature)
```

### Rate Limiting
* 100 messages per second per peer
* 1000 state syncs per hour
* Exponential backoff on failure

## Failure Handling

### Timeouts

* Gossip timeout: 500ms
* Connection timeout: 3000ms
* Sync timeout: 5000ms

### Retry Strategy

* 3 retries with exponential backoff
* Jitter added to prevent stampedes

## Version Compatibility

### Semantic Versioning

* Major version: Breaking changes
* Minor version: New features (backward compatible)
* Patch version: Bug fixes

### Version Negotiation

Nodes exchange version information during handshake:

```text
handshake = {
    "version": "1.0.0",
    "capabilities": ["gossip", "consensus"],
    "features": ["amplification"]
}
```

## Performance Considerations

### Bandwidth

* Maximum message size: 1MB
* Throttling: 10Mbps per node

### Latency
* Target latency: < 100ms
* Maximum latency: 1000ms

### Throughput

* 1000 messages per second
* 10 consensus rounds per minute

## Monitoring

### Metrics

* Messages sent/received
* Average latency
* Failure rate
* Convergence time
* Consensus rounds

### Logging

```text
[2024-01-15T10:30:45Z] [INFO] Node 0x1234: Gossip received from peer 0x5678
[2024-01-15T10:30:46Z] [WARN] Node 0x1234: Peer 0x5678 timeout
[2024-01-15T10:30:47Z] [ERROR] Node 0x1234: Signature verification failed
```
## Implementation Notes
### Python Implementation
```python
class ProtocolHandler:
    async def handle_message(self, message):
        # Validate message
        if not self.validate_signature(message):
            return

        # Handle by type
        if message.type == MessageType.GOSSIP:
            await self.handle_gossip(message)
        elif message.type == MessageType.PROPOSAL:
            await self.handle_proposal(message)
        # ... handle other types

    async def send_gossip(self, peer_address, state):
        # Create message
        message = self.create_gossip_message(state)

        # Sign message
        message.signature = self.sign(message)

        # Send to peer
        await self.transport.send(peer_address, message)
```

## Future Extensions
1. Sharding: Support for sharded consensus
2. Snapshots: State checkpointing for faster sync
3. Hybrid Consensus: Combined with other consensus mechanisms
4. Cross-chain: Interoperability with other networks
5. Privacy: Zero-knowledge proofs for hypothesis evaluation
