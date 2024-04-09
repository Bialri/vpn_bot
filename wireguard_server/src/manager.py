from wireguard_manager import WGManager
from .config import WG_CONFIG_DIR, WG_CONFIG_PREFIX, WG_NETWORK_PREFIX


POSTUP_TEMPLATES = ['iptables -I INPUT -p udp -j ACCEPT',
                    'iptables -I FORWARD -i ens3 -o %i -j ACCEPT',
                    'iptables -I FORWARD -i %i', 'iptables -t nat -A POSTROUTING -o ens3 -j MASQUERADE',
                    'ip6tables -I FORWARD -i %i -j ACCEPT', 'ip6tables -t nat -A POSTROUTING -o ens3 -j MASQUERADE']

POSTDOWN_TEMPLATES = ['iptables -D INPUT -p udp -j ACCEPT',
                      'iptables -D FORWARD -i ens3 -o %i -j ACCEPT',
                      'iptables -D FORWARD -i %i -j ACCEPT', 'iptables -t nat -D POSTROUTING -o ens3 -j MASQUERADE',
                      'ip6tables -D FORWARD -i %i -j ACCEPT', 'ip6tables -t nat -D POSTROUTING -o ens3 -j MASQUERADE']

manager = WGManager(WG_NETWORK_PREFIX, WG_CONFIG_DIR, WG_CONFIG_PREFIX, default_post_up_commands=POSTDOWN_TEMPLATES,
                    default_post_down_commands=POSTDOWN_TEMPLATES)