from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import ForeignKey

from src.bot.database import Base


class VPNInterface(Base):
    __tablename__ = 'vpn_interfaces'
    __table_args__ = {'extend_existing': True}
    id: Mapped[int] = mapped_column(primary_key=True)
    interface_name: Mapped[str]
    server_id: Mapped[int] = mapped_column(ForeignKey('vpn_servers.id'))
    server: Mapped['Server'] = relationship(back_populates='interfaces')
    owner_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    owner: Mapped['User'] = relationship(back_populates='vpn_interfaces')


class Server(Base):
    __tablename__ = 'vpn_servers'
    __table_args__ = {'extend_existing': True}
    id: Mapped[int] = mapped_column(primary_key=True)
    address: Mapped[str]
    country: Mapped[str]
    interfaces: Mapped[list["VPNInterface"]] = relationship(back_populates='server')
