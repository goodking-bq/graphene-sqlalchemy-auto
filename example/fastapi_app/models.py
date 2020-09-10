from sqlalchemy import *
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from database import Base


user_role = Table(
    "user_role", Base.metadata,
    Column("user_id", Integer, ForeignKey(
        "user.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("role.id"), primary_key=True)
)


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(String(20))
    password = Column(String(100), nullable=False)
    roles = relationship("Role", secondary="user_role",
                         back_populates="users")


class Role(Base):
    __tablename__ = "role"
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    users = relationship("User", secondary="user_role",
                         back_populates="roles")


class Article(Base):
    __tablename__ = "article"
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(String(255))
    author_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    tags = Column(String(255))
    text = Column(Text(), nullable=False)
    create_time = Column(DateTime, default=func.now())
    update_time = Column(
        DateTime, default=func.now(), onupdate=func.now(), doc=u"更新时间"
    )
