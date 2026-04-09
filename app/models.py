from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, ForeignKey
from app.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_admin: Mapped[bool] = mapped_column(default=False)

    posts = relationship("BlogPost", back_populates="author", cascade="all, delete")
    comments = relationship("Comment", back_populates="comment_author", cascade="all, delete")

    def __repr__(self):
        return f"<User {self.email}>"


class BlogPost(db.Model):
    __tablename__ = "blog_posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(100), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    author = relationship("User", back_populates="posts")

    comments = relationship("Comment", back_populates="parent_post", cascade="all, delete")

    def __repr__(self):
        return f"<BlogPost {self.title}>"


class Comment(db.Model):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    comment_author = relationship("User", back_populates="comments")

    post_id: Mapped[int] = mapped_column(ForeignKey("blog_posts.id"), nullable=False)
    parent_post = relationship("BlogPost", back_populates="comments")

    def __repr__(self):
        return f"<Comment {self.id}>"