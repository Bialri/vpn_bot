from wireguard_manager import WGManager
from pathlib import Path

CONFIG_DIR = Path('/etc/wireguard/')
CONFIG_PREFIX = 'wg0'
DEFAULT_NETWORK_PREFIX = 28
POSTUP_TEMPLATES = ['iptables -I INPUT -p udp -j ACCEPT',
          'iptables -I FORWARD -i ens3 -o %i -j ACCEPT',
          'iptables -I FORWARD -i %i', 'iptables -t nat -A POSTROUTING -o ens3 -j MASQUERADE',
          'ip6tables -I FORWARD -i %i -j ACCEPT', 'ip6tables -t nat -A POSTROUTING -o ens3 -j MASQUERADE']

POSTDOWN_TEMPLATES = ['iptables -D INPUT -p udp -j ACCEPT',
            'iptables -D FORWARD -i ens3 -o %i -j ACCEPT',
            'iptables -D FORWARD -i %i -j ACCEPT', 'iptables -t nat -D POSTROUTING -o ens3 -j MASQUERADE',
            'ip6tables -D FORWARD -i %i -j ACCEPT', 'ip6tables -t nat -D POSTROUTING -o ens3 -j MASQUERADE']

manager = WGManager(DEFAULT_NETWORK_PREFIX, default_post_up_commands=POSTDOWN_TEMPLATES, default_post_down_commands=POSTDOWN_TEMPLATES)