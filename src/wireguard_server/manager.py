from wireguard_manager.manager import WGManager
from pathlib import Path

CONFIG_DIR = Path('/etc/wireguard/')
CONFIG_PREFIX = 'wg0'
DEFAULT_NETWORK_PREFIX = 28
POSTUP_TEMPLATES = ['iptables -I INPUT -p udp --dport %wg_port -j ACCEPT',
          'iptables -I FORWARD -i ens3 -o %wg_interface -j ACCEPT',
          'iptables -I FORWARD -i %wg_interface -j ACCEPT', 'iptables -t nat -A POSTROUTING -o ens3 -j MASQUERADE',
          'ip6tables -I FORWARD -i %wg_interface -j ACCEPT', 'ip6tables -t nat -A POSTROUTING -o ens3 -j MASQUERADE']

POSTDOWN_TEMPLATES = ['iptables -D INPUT -p udp --dport %wg_port -j ACCEPT',
            'iptables -D FORWARD -i ens3 -o %wg_interface -j ACCEPT',
            'iptables -D FORWARD -i %wg_interface -j ACCEPT', 'iptables -t nat -D POSTROUTING -o ens3 -j MASQUERADE',
            'ip6tables -D FORWARD -i %wg_interface -j ACCEPT', 'ip6tables -t nat -D POSTROUTING -o ens3 -j MASQUERADE']

manager = WGManager(CONFIG_DIR,
                    CONFIG_PREFIX,
                    DEFAULT_NETWORK_PREFIX,
                    POSTUP_TEMPLATES,
                    POSTDOWN_TEMPLATES)