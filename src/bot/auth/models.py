from datetime import datetime, date

from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.bot.database import Base


class User(Base):
    __tablename__= 'user'
    __table_args__ = {'extend_existing': True}
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    registered_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(default=False)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    subscription_till: Mapped[date] = mapped_column(default=date.today())
    vpn_interfaces: Mapped[list['VPNInterface']] = relationship(back_populates='owner', lazy='joined')
