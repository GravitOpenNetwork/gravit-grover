# Security Architecture

## Overview

Gravit Grover Network implements comprehensive security measures to ensure:
1. **Authenticity**: Nodes are who they claim to be
2. **Integrity**: Messages cannot be tampered with
3. **Confidentiality**: Sensitive information is protected
4. **Availability**: Network remains operational under attack
5. **Reputation**: Nodes are evaluated based on behavior

## Threat Model

### Adversarial Capabilities

1. **Eavesdropping**: Intercept communication
2. **Message Tampering**: Modify messages in transit
3. **Identity Spoofing**: Impersonate legitimate nodes
4. **Sybil Attacks**: Create multiple identities
5. **Eclipse Attacks**: Isolate nodes from the network
6. **Fault Injection**: Send corrupt messages
7. **Denial of Service**: Flood the network

### Trust Assumptions

1. **Honest Majority**: At least 2/3 of nodes are honest
2. **Secure Crypto**: Cryptographic primitives are secure
3. **Network Reliable**: Communication channels are available

## Cryptographic Foundation

### Digital Signatures

```python
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ed25519

class Signature:
    @staticmethod
    def generate_keypair() -> tuple:
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        return private_key, public_key

    @staticmethod
    def sign(private_key: ed25519.Ed25519PrivateKey,
             message: bytes) -> bytes:
        return private_key.sign(message)

    @staticmethod
    def verify(public_key: ed25519.Ed25519PublicKey,
               message: bytes,
               signature: bytes) -> bool:
        try:
            public_key.verify(signature, message)
            return True
        except:
            return False
```

### Hash Functions

```python
import hashlib
import json

def compute_hash(data: dict) -> str:
    """Compute cryptographic hash of data."""
    data_string = json.dumps(data, sort_keys=True)
    return hashlib.sha256(data_string.encode()).hexdigest()
```

## Node Identity

### Identity Structure
```python
class NodeIdentity:
    def __init__(self, node_id: str, public_key: bytes):
        self.node_id = node_id
        self.public_key = public_key
        self.created_at = datetime.utcnow()

    def to_dict(self) -> dict:
        return {
            'node_id': self.node_id,
            'public_key': self.public_key.hex(),
            'created_at': self.created_at.isoformat()
        }
```

### Identity Verification

```python
def verify_identity(identity_dict: dict, signature: bytes) -> bool:
    """
    Verify node identity using public key.
    """
    # Extract public key
    public_key = ed25519.Ed25519PublicKey.from_public_bytes(
        bytes.fromhex(identity_dict['public_key'])
    )

    # Verify signature
    message = json.dumps(identity_dict).encode()
    return Signature.verify(public_key, message, signature)
```

## Message Security

### Secure Message Format

```python
class SecureMessage:
    def __init__(self, type: str, payload: bytes,
                 sender: str, timestamp: int):
        self.type = type
        self.payload = payload
        self.sender = sender
        self.timestamp = timestamp
        self.signature = None

    def sign(self, private_key):
        """Sign the message."""
        content = self._get_content()
        self.signature = Signature.sign(private_key, content)

    def verify(self, public_key) -> bool:
        """Verify message signature."""
        if not self.signature:
            return False
        content = self._get_content()
        return Signature.verify(public_key, content, self.signature)

    def _get_content(self) -> bytes:
        """Get message content for signing."""
        data = {
            'type': self.type,
            'payload': self.payload.hex(),
            'sender': self.sender,
            'timestamp': self.timestamp
        }
        return json.dumps(data, sort_keys=True).encode()
```

## Reputation System

### Node Reputation

```python
class ReputationManager:
    def __init__(self):
        self.reputations = {}

    def update_reputation(self, node_id: str,
                         behavior_score: float,
                         weight: float = 0.1):
        """Update node reputation based on behavior."""
        if node_id not in self.reputations:
            self.reputations[node_id] = 0.5

        # Update with moving average
        self.reputations[node_id] = (
            self.reputations[node_id] * (1 - weight) +
            behavior_score * weight
        )

        # Clip to [0, 1]
        self.reputations[node_id] = max(0, min(1, self.reputations[node_id]))

    def get_reputation(self, node_id: str) -> float:
        """Get node reputation."""
        return self.reputations.get(node_id, 0.5)
```

### Penalty System

```python
def apply_penalty(node_id: str, offense: str, severity: float):
    """
    Apply penalty to node based on offense.
    """
    penalties = {
        'signature_failure': -0.2,
        'spam': -0.3,
        'inconsistent_behavior': -0.4,
        'malicious_activity': -1.0
    }

    penalty = penalties.get(offense, -0.1) * severity
    manager.update_reputation(node_id, penalty)
```

## Sybil Resistance

### Proof of Work

```python
def proof_of_work(challenge: bytes, difficulty: int) -> tuple:
    """
    Simple proof of work for Sybil resistance.
    """
    nonce = 0
    while True:
        data = challenge + nonce.to_bytes(8, 'big')
        hash_result = hashlib.sha256(data).digest()
        if int.from_bytes(hash_result, 'big') < 2 ** (256 - difficulty):
            return nonce, hash_result
        nonce += 1
```

### Staking Mechanism

```python
class StakingSystem:
    def __init__(self, required_stake: int = 1000):
        self.required_stake = required_stake
        self.stakes = {}

    def stake(self, node_id: str, amount: int):
        """Stake tokens for node."""
        if amount < self.required_stake:
            raise ValueError(f"Minimum stake: {self.required_stake}")
        self.stakes[node_id] = amount

    def get_stake(self, node_id: str) -> int:
        return self.stakes.get(node_id, 0)

    def slash(self, node_id: str, reason: str):
        """Slash node's stake for misbehavior."""
        if node_id in self.stakes:
            self.stakes[node_id] *= 0.5  # Slash 50%
```

## Attack Mitigation

### Rate Limiting

```python
class RateLimiter:
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []

    def check(self, node_id: str) -> bool:
        """Check if rate limit is exceeded."""
        now = time.time()
        self.requests = [r for r in self.requests if r > now - self.time_window]
        self.requests.append(now)
        return len(self.requests) <= self.max_requests
```

### Blacklisting

```python
class Blacklist:
    def __init__(self):
        self.blacklisted_nodes = set()
        self.blacklist_expiry = {}

    def add(self, node_id: str, duration: int = 3600):
        """Add node to blacklist."""
        self.blacklisted_nodes.add(node_id)
        self.blacklist_expiry[node_id] = time.time() + duration

    def is_blacklisted(self, node_id: str) -> bool:
        """Check if node is blacklisted."""
        if node_id in self.blacklist_expiry:
            if time.time() > self.blacklist_expiry[node_id]:
                self.blacklisted_nodes.remove(node_id)
                return False
            return True
        return False
```

## Security Auditing

### Audit Log

```python
class AuditLogger:
    def __init__(self):
        self.logs = []

    def log_event(self, node_id: str, event_type: str,
                 details: dict):
        """Log security event."""
        self.logs.append({
            'timestamp': datetime.utcnow().isoformat(),
            'node_id': node_id,
            'event_type': event_type,
            'details': details
        })

    def get_events(self, node_id: str = None) -> list:
        """Get audit events."""
        if node_id:
            return [l for l in self.logs if l['node_id'] == node_id]
        return self.logs
```

## Best Practices
1. Always verify signatures before accepting messages
2. Use strong randomness for nonce generation
3. Rotate cryptographic keys periodically
4. Monitor reputation scores for anomalies
5. Rate limit incoming messages to prevent DoS
6. Maintain audit logs for forensic analysis
7. Implement timeout mechanisms for state sync
8. Use secure communication channels (TLS/SSL)

## References
1. Lamport, L., Shostak, R., & Pease, M. (1982). The Byzantine generals problem.
2. Bender, M. A., & Katz, J. (2016). Introduction to cryptography.
3. Nakamoto, S. (2008). Bitcoin: A peer-to-peer electronic cash system.
4. Buterin, V. (2014). A next-generation smart contract and decentralized application platform.
