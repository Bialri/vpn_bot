import ipaddress
from typing import Tuple

from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives import serialization
import codecs
from pathlib import Path
import os
import subprocess

from peer import WGPeer
from core import WGUtilsMixin


class WGInterface(WGUtilsMixin):
    def __init__(self,
                 interface_name: str = None,
                 address: ipaddress.IPv4Network | str = None,
                 listen_port: int = None,
                 private_key: X25519PrivateKey = None,
                 dns: ipaddress.IPv4Address | str = None,
                 mtu: int = None,
                 post_up_commands: list[str] = None,
                 post_down_commands: list[str] = None,
                 peers: list[WGPeer] = None,
                 config_dir: Path | str = None) -> None:
        self.name = interface_name
        if isinstance(address, str):
            address = ipaddress.ip_network(address, strict=False)
        self.address = address
        self.listen_port = listen_port
        self.private_key = private_key
        if dns is not None and isinstance(dns, str):
            dns = ipaddress.ip_address(dns)
        self.dns = dns
        self.mtu = mtu
        self.post_up_commands = post_up_commands
        if not post_up_commands:
            self.post_up_commands = []
        self.post_down_commands = post_down_commands
        if not post_down_commands:
            self.post_down_commands = []
        self.peers = peers
        if not peers:
            self.peers = []
        if isinstance(config_dir, str):
            config_dir = Path(config_dir)
        self.config_dir = config_dir

    @classmethod
    def load_existing(cls, configuration_path: Path | str) -> "WGInterface":
        return load_config(configuration_path)

    @classmethod
    def create_new(cls,
                   prefix: str,
                   config_dir: Path | str,
                   dns: ipaddress.IPv4Address | str = None,
                   mtu: int = None,
                   post_up_command_templates: list[str] = None,
                   post_down_command_templates: list[str] = None) -> "WGInterface":
        return create_new_interface(prefix, config_dir, dns, mtu, post_up_command_templates,
                                    post_down_command_templates)

    def convert_command_templates(self, command_templates: list[str]) -> tuple[str, ...]:
        commands = []
        for command_template in command_templates:
            command_template = command_template.replace('%wg_interface', self.name)
            command = command_template.replace('%wg_port', str(self.listen_port))
            commands.append(command)
        return tuple(commands)

    @staticmethod
    def _get_matching_config_line(configuration_path: Path, option: str) -> str | None:
        with open(configuration_path, 'r') as file:
            for line in file:
                if option in line:
                    value = line.split('= ', 1)[1].rstrip()
                    return value
        return None

    @staticmethod
    def _get_matching_config_lines(configuration_path: Path, option: str) -> list[str]:
        with open(configuration_path, 'r') as file:
            values = []
            for line in file:
                if option in line:
                    value = line.split('= ', 1)[1].rstrip()
                    values.append(value)
            return values

    def _config_address(self, configuration_path: Path) -> ipaddress.IPv4Network | None:
        value = self._get_matching_config_line(configuration_path, 'Address')
        if value:
            return ipaddress.ip_network(value, strict=False)
        return None

    @staticmethod
    def _config_name(configuration_path: Path) -> str:
        filename = configuration_path.name
        return filename.split('.')[0]

    def _config_listen_port(self, configuration_path: Path) -> int | None:
        value = self._get_matching_config_line(configuration_path, 'ListenPort')
        if value:
            return int(value)
        return None

    def _config_private_key(self, configuration_path: Path) -> X25519PrivateKey | None:
        value = self._get_matching_config_line(configuration_path, 'PrivateKey')
        if value:
            decoded_key = codecs.decode(value.encode('utf8'), 'base64')
            private_key = X25519PrivateKey.from_private_bytes(decoded_key)
            return private_key
        return None

    def _config_dns(self, configuration_path: Path) -> ipaddress.IPv4Address | None:
        value = self._get_matching_config_line(configuration_path, 'DNS')
        if value:
            return ipaddress.IPv4Address(value)
        return None

    def _config_mtu(self, configuration_path: Path) -> int | None:
        value = self._get_matching_config_line(configuration_path, 'MTU')
        if value:
            return int(value)
        return None

    def _config_postup_commands(self, configuration_path: Path) -> list[str]:
        values = self._get_matching_config_lines(configuration_path, 'PostUp')
        return values

    def _config_postdown_commands(self, configuration_path: Path) -> list[str]:
        values = self._get_matching_config_lines(configuration_path, 'PostDown')
        return values

    @staticmethod
    def _config_peers(configuration_path: Path) -> list[WGPeer]:
        with open(configuration_path, 'r') as file:
            config = file.read()
            peer_configs = config.split('[Peer]')[1:]
            peers = []
            for peer_config in peer_configs:
                peer = WGPeer.from_config(peer_config)
                peers.append(peer)
            return peers

    def _free_ips(self) -> list[ipaddress.IPv4Network]:
        ip_range = list(self.address.subnets(new_prefix=32))[1:]
        occupied_addresses = [peer.allowed_ips for peer in self.peers]
        ip_range = list(filter(lambda x: x not in occupied_addresses, ip_range))
        return ip_range

    def add_peer(self, peer) -> None:
        self.peers.append(peer)

    def delete_peer(self, peer):
        self.peers.remove(peer)

    def create_peer(self) -> WGPeer:
        allowed_ips = min(self._free_ips())
        peer = WGPeer(allowed_ips=allowed_ips)
        peer.generate_key()
        self.peers.append(peer)
        return peer

    def save_config(self) -> None:
        config_path = os.path.join(self.config_dir, f'{self.name}.conf')
        with open(config_path, 'w') as file:
            file.write(self.generate_config())

    @staticmethod
    def _generate_config_line(option: str, value: str | None) -> str:
        if value:
            return f'{option} = {str(value)}\n'
        return ''

    def _generate_config_lines(self, option: str, values: list[str]) -> str:
        if values:
            return ''.join([f'{option} = {str(value)}\n' for value in values])
        return ''

    def generate_config(self) -> str:
        address = self._generate_config_line('Address', str(self.address))
        listen_port = self._generate_config_line('ListenPort', str(self.listen_port))

        if self.private_key:
            bytes_ = self.private_key.private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption()
            )
            private_key = codecs.encode(bytes_, 'base64').decode('utf8').strip()
            private_key = self._generate_config_line("PrivateKey", private_key)
        else:
            private_key = ''

        dns = self._generate_config_line('DNS', self.dns)
        mtu = self._generate_config_line('MTU', self.mtu)

        post_up = self._generate_config_lines('PostUp', self.post_up_commands)
        post_down = self._generate_config_lines('PostDown', self.post_down_commands)

        peers = '\n\n'.join([peer.generate_peer_config() for peer in self.peers])
        config = f'[Interface]\n{address}{listen_port}{private_key}{dns}{mtu}{post_up}{post_down}\n\n{peers}'
        return config

    def generate_peer_config(self,
                             peer: WGPeer,
                             allowed_ips: ipaddress.IPv4Network = ipaddress.ip_network('0.0.0.0/0', strict=False),
                             domain_name: str = None):
        if peer in self.peers:
            peer_interface = peer.generate_interface_config()
            if self.private_key:
                public_key = self.private_key.public_key().public_bytes(encoding=serialization.Encoding.Raw,
                                                                        format=serialization.PublicFormat.Raw)
                public_encoded = codecs.encode(public_key, 'base64').decode('utf8').strip()
                public_key = self._generate_config_line("PublicKey", public_encoded)
            else:
                public_key = ''

            allowed_ips = self._generate_config_line("AllowedIPs", str(allowed_ips))

            if not domain_name:
                domain_name = self._get_host_ip()
            port = self.listen_port
            interface_socket = f'{domain_name}:{port}'
            interface_socket = self._generate_config_line('Endpoint', interface_socket)

            config = f'{peer_interface}[Peer]\n{public_key}{allowed_ips}{interface_socket}'
            return config

    def update_config(self) -> None:
        subprocess.run(['wg', 'syncconf', self.name, '<', '(', 'wg-quick', 'strip', self.name, ')'],
                       capture_output=True)

    def run_interface(self) -> None:
        config_path = os.path.join(self.config_dir, f'{self.name}.conf')
        subprocess.run(['wg-quick', 'up', config_path])

    def stop_interface(self) -> None:
        config_path = os.path.join(self.config_dir, f'{self.name}.conf')
        subprocess.run(['wg-quick', 'down', config_path])

def load_config(configuration_path: Path | str) -> WGInterface:
    interface = WGInterface()
    if isinstance(configuration_path, str):
        configuration_path = Path(configuration_path)
    if not configuration_path.exists():
        raise Exception
    interface.config_dir = os.path.dirname(configuration_path)
    interface.address = interface._config_address(configuration_path)
    interface.name = interface._config_name(configuration_path)
    interface.listen_port = interface._config_listen_port(configuration_path)
    interface.private_key = interface._config_private_key(configuration_path)
    interface.dns = interface._config_dns(configuration_path)
    interface.mtu = interface._config_mtu(configuration_path)
    interface.post_up_commands = interface._config_postup_commands(configuration_path)
    interface.post_down_commands = interface._config_postdown_commands(configuration_path)
    interface.peers = interface._config_peers(configuration_path)
    return interface


def create_new_interface(prefix: str,
                         config_dir: Path | str,
                         dns: ipaddress.IPv4Address | str = None,
                         mtu: int = None,
                         post_up_command_templates: list[str] = None,
                         post_down_command_templates: list[str] = None) -> "WGInterface":
    interface = WGInterface()
    if isinstance(config_dir, str):
        config_dir = Path(config_dir)
    interface.config_dir = config_dir
    interface.name = interface._get_free_interface_name(config_dir, prefix)
    interface.address = interface._get_free_subnetwork(config_dir)
    interface.listen_port = interface._get_free_port(config_dir)
    interface.private_key = interface._generate_private_key()
    if isinstance(dns, str):
        dns = ipaddress.ip_address(dns)
    interface.dns = dns
    interface.mtu = mtu
    if not post_up_command_templates:
        post_up_commands = []
    else:
        post_up_commands = interface.convert_command_templates(post_up_command_templates)
    interface.post_up_commands = post_up_commands

    if not post_down_command_templates:
        post_down_commands = []
    else:
        post_down_commands = interface.convert_command_templates(post_down_command_templates)
    interface.post_down_commands = post_down_commands
    return interface


path = Path("/etc/wireguard/")
postup = ['iptables -I INPUT -p udp --dport %wg_port -j ACCEPT',
          'iptables -I FORWARD -i ens3 -o %wg_interface -j ACCEPT',
          'iptables -I FORWARD -i %wg_interface -j ACCEPT', 'iptables -t nat -A POSTROUTING -o ens3 -j MASQUERADE',
          'ip6tables -I FORWARD -i %wg_interface -j ACCEPT', 'ip6tables -t nat -A POSTROUTING -o ens3 -j MASQUERADE']

postdown = ['iptables -D INPUT -p udp --dport %wg_port -j ACCEPT',
            'iptables -D FORWARD -i ens3 -o %wg_interface -j ACCEPT',
            'iptables -D FORWARD -i %wg_interface -j ACCEPT', 'iptables -t nat -D POSTROUTING -o ens3 -j MASQUERADE',
            'ip6tables -D FORWARD -i %wg_interface -j ACCEPT', 'ip6tables -t nat -D POSTROUTING -o ens3 -j MASQUERADE']

interface = WGInterface.create_new("wg", path, post_up_command_templates=postup, post_down_command_templates=postdown)
for _ in range(3):
    peer = interface.create_peer()
interface.save_config()
interface.run_interface()
peer = interface.create_peer()
interface.update_config()
print(interface.generate_peer_config(peer))
