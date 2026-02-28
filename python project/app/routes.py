from flask import render_template, redirect, url_for, flash, request, session
from app import app, db
from app.forms import UserHealthForm
from app.models import User, UserHealthLog
from sqlalchemy.exc import IntegrityError


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form.get("username", "").strip()

        if not username:
            flash("Enter username")
            return render_template("index.html")

        if username.lower() == "admin":
            flash("Admin login")
            return redirect(url_for("admin"))

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            current_user = existing_user
        else:
            current_user = User(username=username)
            db.session.add(current_user)
            db.session.commit()

        session["user_id"] = current_user.id
        flash(f"Logged in as {current_user.username}")
        return redirect(url_for("user"))

    return render_template("index.html")

@app.route("/user", methods=["GET", "POST"])
def user():
    user_id = session.get("user_id")

    if not user_id:
        flash("Please enter a username first")
        return redirect(url_for("index"))

    current_user = db.session.get(User, user_id)

    if current_user is None:
        session.pop("user_id", None)
        flash("User not found")
        return redirect(url_for("index"))

    form = UserHealthForm()

    if form.validate_on_submit():
        event = UserHealthLog(
            user_id=current_user.id,
            log_date=form.log_date.data,
            steps=form.steps.data,
            sleep=form.sleep.data,
            blood=form.blood.data,
            heart=form.heart.data,
            user_comment=form.user_comment.data,
        )

        try:
            db.session.add(event)
            db.session.commit()
            flash("Log successfully added")
            return redirect(url_for("user"))
        except IntegrityError:
            db.session.rollback()
            flash("Log already exists for this date")

    user_health_logs = (
        UserHealthLog.query
        .filter_by(user_id=current_user.id)
        .order_by(UserHealthLog.log_date.desc())
        .all()
    )

    return render_template(
        "user.html",
        form=form,
        logs=user_health_logs,
        username=current_user.username,
    )

@app.route("/admin", methods=["GET", "POST"])
def admin():
    users = User.query.order_by(User.username.asc()).all()
    #logs = UserHealthLog.query.order_by(UserHealthLog.log_date.desc()).all()

    return render_template("admin.html", users=users)#, logs=logs)

@app.route("/delete_user/<int:user_id>")
def delete_user(user_id):
    user_to_delete = User.query.get_or_404(user_id)
    db.session.delete(user_to_delete)
    db.session.commit()
    flash("User deleted")
    return redirect(url_for("admin"))

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Logged out")
    return redirect(url_for("index"))