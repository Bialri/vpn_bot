import ipaddress
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives import serialization
import codecs
from core import WGUtilsMixin


class WGPeer(WGUtilsMixin):
    def __init__(self,
                 allowed_ips: ipaddress.IPv4Network | str = None,
                 private_key: X25519PrivateKey = None) -> None:
        if isinstance(allowed_ips, str):
            allowed_ips = ipaddress.ip_network(allowed_ips, strict=False)
        self.allowed_ips = allowed_ips
        self.private_key = private_key

    def generate_interface_config(self) -> str:
        if self.private_key:
            bytes_ = self.private_key.private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption()
            )
            private_encoded = codecs.encode(bytes_, 'base64').decode('utf8').strip()
            private_key = f'PrivateKey = {private_encoded}\n'
        if self.allowed_ips:
            allowed_ips = f'Address = {str(self.allowed_ips)}\n'
        config = f'[Interface]\n{allowed_ips}{private_key}'
        return config

    def generate_peer_config(self,dns: ipaddress.IPv4Address = ipaddress.IPv4Address('1.1.1.1')) -> str:
        if self.private_key:
            bytes_ = self.private_key.private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption()
            )
            private_encoded = codecs.encode(bytes_, 'base64').decode('utf8').strip()
            public_key = self.private_key.public_key().public_bytes(encoding=serialization.Encoding.Raw,
                                                                    format=serialization.PublicFormat.Raw)
            public_encoded = codecs.encode(public_key, 'base64').decode('utf8').strip()
            public_key = f'PublicKey = {public_encoded}\n'
            private_key = f'# PrivateKey = {private_encoded}\n'
        else:
            public_key = ''
            private_key = ''

        dns = f'DNS = {str(dns)}\n'

        if self.allowed_ips:
            allowed_ips = f'AllowedIPs = {str(self.allowed_ips)}\n'

        config = f'[Peer]\n{public_key}{allowed_ips}{private_key}{dns}\n\n'
        return config

    @classmethod
    def from_config(cls, peer_config: str) -> "WGPeer":
        return peer_from_config(peer_config)

    @staticmethod
    def _private_key_config(peer_config: str) -> X25519PrivateKey | None:
        lines = peer_config.split('\n')
        for line in lines:
            if '# PrivateKey' in line:
                value = line.split('= ', 1)[1].rstrip()
                decoded_key = codecs.decode(value.encode('utf8'), 'base64')
                private_key = X25519PrivateKey.from_private_bytes(decoded_key)
                return private_key
        return None

    @staticmethod
    def _allowed_ips_config(peer_config: str) -> ipaddress.IPv4Network | None:
        lines = peer_config.split('\n')
        for line in lines:
            if 'AllowedIPs' in line:
                value = line.split('= ', 1)[1].rstrip()
                return ipaddress.ip_network(value, False)
        return None

    def generate_key(self) -> None:
        self.private_key = self._generate_private_key()


def peer_from_config(peer_config: str) -> WGPeer:
    peer = WGPeer()
    peer.private_key = peer._private_key_config(peer_config)
    peer.allowed_ips = peer._allowed_ips_config(peer_config)
    return peer
