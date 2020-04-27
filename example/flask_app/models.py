from sqlalchemy import func
from sqlalchemy.ext.associationproxy import association_proxy

from .extensions import db

user_role = db.Table(
    "user_role",
    db.metadata,
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("role_id", db.Integer, db.ForeignKey("role.id")),
    db.UniqueConstraint("user_id", "role_id"),
)


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    password = db.Column(db.String(100), nullable=False)
    roles = db.relationship("Role", secondary=user_role, back_populates="users")
    role_names = key_ids = association_proxy("roles", "name")


class Role(db.Model):
    __tablename__ = "role"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

    users = db.relationship("User", secondary=user_role, back_populates="roles")


class Article(db.Model):
    __tablename__ = "article"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    tags = db.Column(db.String(255))
    text = db.Column(db.Text(), nullable=False)
    create_time = db.Column(db.DateTime, default=func.now())
    update_time = db.Column(
        db.DateTime, default=func.now(), onupdate=func.now(), doc=u"更新时间"
    )
