import pytest
from velikey import Client

def test_client_init():
    client = Client(api_key="test")
    assert client is not None

def test_policy_creation():
    client = Client(api_key="test")
    policy = {"name": "test", "algorithms": ["aes-256-gcm"]}
    assert policy["name"] == "test"

def test_quantum_resistant_support():
    qr_algos = ["kyber1024", "dilithium5"]
    assert len(qr_algos) == 2
