from datetime import date

from flask import render_template, redirect, url_for, flash, request
from flask_mail import Message
from app.extensions import mail
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db
from app.forms import CreatePostForm, RegisterForm, LoginForm, CommentForm
from app.models import User, BlogPost, Comment
from app.utils import admin_only


def register_routes(app):

    @app.route("/")
    def get_all_posts():
        result = db.session.execute(db.select(BlogPost).order_by(BlogPost.id.desc()))
        posts = result.scalars().all()
        return render_template("index.html", all_posts=posts)

    @app.route("/register", methods=["GET", "POST"])
    def register():
        form = RegisterForm()

        if form.validate_on_submit():
            existing_user = db.session.execute(
                db.select(User).where(User.email == form.email.data)
            ).scalar()

            if existing_user:
                flash("You've already signed up with that email. Please log in instead.", "warning")
                return redirect(url_for("login"))

            hashed_password = generate_password_hash(
                form.password.data,
                method="pbkdf2:sha256",
                salt_length=8
            )

            # First registered user becomes admin
            user_count = db.session.execute(db.select(User)).scalars().all()
            is_first_user = len(user_count) == 0

            new_user = User(
                email=form.email.data,
                name=form.name.data,
                password=hashed_password,
                is_admin=is_first_user
            )

            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)
            flash("Registration successful!", "success")
            return redirect(url_for("get_all_posts"))

        return render_template("register.html", form=form)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        form = LoginForm()

        if form.validate_on_submit():
            user = db.session.execute(
                db.select(User).where(User.email == form.email.data)
            ).scalar()

            if not user:
                flash("That email does not exist.", "danger")
                return redirect(url_for("login"))

            if not check_password_hash(user.password, form.password.data):
                flash("Incorrect password. Please try again.", "danger")
                return redirect(url_for("login"))

            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for("get_all_posts"))

        return render_template("login.html", form=form)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("Logged out successfully.", "info")
        return redirect(url_for("get_all_posts"))

    @app.route("/post/<int:post_id>", methods=["GET", "POST"])
    def show_post(post_id):
        requested_post = db.get_or_404(BlogPost, post_id)
        comment_form = CommentForm()

        if comment_form.validate_on_submit():
            if not current_user.is_authenticated:
                flash("You need to log in or register to comment.", "warning")
                return redirect(url_for("login"))

            new_comment = Comment(
                text=comment_form.comment_text.data,
                comment_author=current_user,
                parent_post=requested_post
            )
            db.session.add(new_comment)
            db.session.commit()
            flash("Comment added successfully!", "success")
            return redirect(url_for("show_post", post_id=post_id))

        return render_template("post.html", post=requested_post, form=comment_form)

    @app.route("/new-post", methods=["GET", "POST"])
    @login_required
    @admin_only
    def add_new_post():
        form = CreatePostForm()

        if form.validate_on_submit():
            new_post = BlogPost(
                title=form.title.data,
                subtitle=form.subtitle.data,
                body=form.body.data,
                img_url=form.img_url.data,
                author=current_user,
                date=date.today().strftime("%B %d, %Y")
            )
            db.session.add(new_post)
            db.session.commit()
            flash("New post created successfully!", "success")
            return redirect(url_for("get_all_posts"))

        return render_template("make-post.html", form=form, is_edit=False)

    @app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
    @login_required
    @admin_only
    def edit_post(post_id):
        post = db.get_or_404(BlogPost, post_id)

        edit_form = CreatePostForm(
            title=post.title,
            subtitle=post.subtitle,
            img_url=post.img_url,
            body=post.body
        )

        if edit_form.validate_on_submit():
            post.title = edit_form.title.data
            post.subtitle = edit_form.subtitle.data
            post.img_url = edit_form.img_url.data
            post.body = edit_form.body.data

            db.session.commit()
            flash("Post updated successfully!", "success")
            return redirect(url_for("show_post", post_id=post.id))

        return render_template("make-post.html", form=edit_form, is_edit=True)

    @app.route("/delete/<int:post_id>", methods=["POST"])
    @login_required
    @admin_only
    def delete_post(post_id):
        post_to_delete = db.get_or_404(BlogPost, post_id)
        db.session.delete(post_to_delete)
        db.session.commit()
        flash("Post deleted successfully.", "success")
        return redirect(url_for("get_all_posts"))

    @app.route("/about")
    def about():
        return render_template("about.html")

    @app.route("/contact", methods=["GET", "POST"])
    def contact():
        if request.method == "POST":
            name = request.form.get("name")
            email = request.form.get("email")
            phone = request.form.get("phone")
            message_body = request.form.get("message")

            try:
                msg = Message(
                    subject=f"New Contact Form Message from {name}",
                    recipients=[app.config["MAIL_USERNAME"]]
                )

                msg.body = f"""
    You received a new contact form message.

    Name: {name}
    Email: {email}
    Phone: {phone}

    Message:
    {message_body}
    """
                mail.send(msg)
                flash("Your message has been sent successfully!")
                return render_template("contact.html", msg_sent=True)

            except Exception as e:
                print("Mail Error:", e)
                flash("Something went wrong. Please try again later.")
                return render_template("contact.html", msg_sent=False)

        return render_template("contact.html", msg_sent=False)

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("403.html"), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("500.html"), 500