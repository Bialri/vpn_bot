from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
import socket
import ipaddress
from pathlib import Path
import os


class WGUtilsMixin:
    @staticmethod
    def _generate_private_key() -> X25519PrivateKey:
        return X25519PrivateKey.generate()

    @staticmethod
    def _get_host_ip() -> str:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return ip_address

    @staticmethod
    def _get_interfaces_addresses(config_dir: Path) -> list[str]:
        interface_paths = config_dir.glob('*.conf')
        addresses = []
        for interface_path in interface_paths:
            with open(interface_path, 'r') as file:
                for line in file:
                    if 'Address = ' in line:
                        address = line.split('= ')[1].rstrip()
                        addresses.append(ipaddress.ip_network(address, strict=False))
        return addresses

    @staticmethod
    def _get_interfaces_names(config_dir: Path) -> list[str]:
        interface_paths = config_dir.glob('*.conf')
        return [interface_path.stem.split('.')[0] for interface_path in interface_paths]

    @staticmethod
    def _get_interfaces_ports(config_dir: Path) -> list[int]:
        interface_paths = list(config_dir.glob('*.conf'))
        ports = []
        for interface_path in interface_paths:
            with open(interface_path, 'r') as file:
                for line in file:
                    if 'ListenPort = ' in line:
                        port = line.split('= ')[1].rstrip()
                        ports.append(int(port))
        return ports

    @classmethod
    def _get_free_port(cls, config_dir: Path) -> int:
        existing_ports = cls._get_interfaces_ports(config_dir)
        for port in range(51820, 65535):
            if port not in existing_ports:
                return port

    @classmethod
    def _get_free_subnetwork(cls, config_dir: Path) -> ipaddress.IPv4Network:
        local_network = ipaddress.ip_network('10.0.0.0/8')
        subnets = list(local_network.subnets(new_prefix=28))
        existing_subnets = cls._get_interfaces_addresses(config_dir)
        subnets = list(filter(lambda x: x not in existing_subnets, subnets))
        return min(subnets)

    @classmethod
    def _get_free_interface_name(cls, config_dir: Path, prefix: str) -> str:
        existing_names = cls._get_interfaces_names(config_dir)
        for i in range(0, 2*16):
            name = f'{prefix}{i}'
            if name not in existing_names:
                return name
