from flask import render_template, redirect, url_for, flash, request, session
from app import app, db
from app.forms import AdminCommentForm, UserHealthForm
from app.models import User, UserHealthLog
from sqlalchemy.exc import IntegrityError


def add_admin_comment_to_log(log_entry, comment_text):
    log_entry.admin_comment = (comment_text or "").strip()
    db.session.commit()


def get_user_logs(user_id, descending=True):
    query = UserHealthLog.query.filter_by(user_id=user_id)

    if descending:
        query = query.order_by(UserHealthLog.log_date.desc())
    else:
        query = query.order_by(UserHealthLog.log_date.asc())

    return query.all()


def build_chart_data(logs):
    return {
        "labels": [log.log_date.strftime("%Y-%m-%d") for log in logs],
        "metrics": [
            {"key": "steps", "label": "Steps", "color": "#1d4ed8", "values": [log.steps for log in logs]},
            {"key": "sleep", "label": "Hours of Sleep", "color": "#059669", "values": [log.sleep for log in logs]},
            {"key": "water", "label": "Water Consumed (Litres)", "color": "#0ea5e9", "values": [log.water for log in logs]},
            {"key": "blood", "label": "Blood Pressure", "color": "#dc2626", "values": [log.blood for log in logs]},
            {"key": "heart", "label": "Heart Rate", "color": "#9333ea", "values": [log.heart for log in logs]},
        ],
    }


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
            water=form.water.data,
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

    user_health_logs = get_user_logs(current_user.id)

    return render_template(
        "user.html",
        form=form,
        logs=user_health_logs,
        username=current_user.username,
    )


@app.route("/user/graph")
def user_graph():
    user_id = session.get("user_id")

    if not user_id:
        flash("Please enter a username first")
        return redirect(url_for("index"))

    current_user = db.session.get(User, user_id)

    if current_user is None:
        session.pop("user_id", None)
        flash("User not found")
        return redirect(url_for("index"))

    user_health_logs = get_user_logs(current_user.id, descending=False)

    return render_template(
        "graph.html",
        user=current_user,
        chart_data=build_chart_data(user_health_logs),
        back_url=url_for("user"),
        back_label="back to user page",
        page_title=f"{current_user.username} Graph",
    )

@app.route("/admin")
def admin():
    users = User.query.order_by(User.username.asc()).all()

    return render_template("admin.html", users=users)


@app.route("/admin/user/<int:user_id>/logs")
def admin_user_logs(user_id):
    selected_user = User.query.get_or_404(user_id)
    user_health_logs = get_user_logs(selected_user.id)

    return render_template(
        "admin_user_logs.html",
        user=selected_user,
        logs=user_health_logs,
    )


@app.route("/admin/user/<int:user_id>/graph")
def admin_user_graph(user_id):
    selected_user = User.query.get_or_404(user_id)
    user_health_logs = get_user_logs(selected_user.id, descending=False)

    return render_template(
        "graph.html",
        user=selected_user,
        chart_data=build_chart_data(user_health_logs),
        back_url=url_for("admin_user_logs", user_id=selected_user.id),
        back_label="back to logs",
        page_title=f"{selected_user.username} Graph",
    )


@app.route("/admin/user/<int:user_id>/logs/<int:log_id>/comment", methods=["GET", "POST"])
def admin_add_comment(user_id, log_id):
    selected_user = User.query.get_or_404(user_id)
    log_entry = UserHealthLog.query.filter_by(
        id=log_id,
        user_id=selected_user.id,
    ).first_or_404()
    form = AdminCommentForm()

    if form.validate_on_submit():
        add_admin_comment_to_log(log_entry, form.admin_comment.data)
        flash("Admin comment saved")
        return redirect(url_for("admin_user_logs", user_id=selected_user.id))

    if request.method == "GET":
        form.admin_comment.data = log_entry.admin_comment

    return render_template(
        "admin_comment.html",
        user=selected_user,
        log=log_entry,
        form=form,
    )

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
