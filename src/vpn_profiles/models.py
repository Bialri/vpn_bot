from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import ForeignKey

from src.database import Base

class VPNProfile(Base):
    __tablename__ = 'vpn_profile'
    __table_args__ = {'extend_existing': True}
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    public_key: Mapped[str]
    allowed_ips: Mapped[str]
    owner_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    owner: Mapped['User'] = relationship(back_populates='vpn_profiles')