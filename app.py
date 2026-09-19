import os
from functools import wraps


from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-key")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///helpdesk.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)


# -----------------------------
# Demo users
# -----------------------------
USERS = {
    "admin": {
        "password": generate_password_hash("admin123"),
        "role": "admin",
        "department": "ICT"
    },
    "ict": {
        "password": generate_password_hash("ict123"),
        "role": "ict",
        "department": "ICT"
    },
    "hr": {
        "password": generate_password_hash("hr123"),
        "role": "employee",
        "department": "HR"
    },
    "finance": {
        "password": generate_password_hash("finance123"),
        "role": "employee",
        "department": "Finance"
    },
    "procurement": {
        "password": generate_password_hash("procurement123"),
        "role": "procurement",
        "department": "Procurement"
    }
}


# -----------------------------
# Ticket model
# -----------------------------
class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)


    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    department = db.Column(db.String(50), nullable=False)   # department that raised the ticket
    priority = db.Column(db.String(20), nullable=False, default="Medium")
    status = db.Column(db.String(30), nullable=False, default="Open")


    created_by = db.Column(db.String(50), nullable=False)
    assigned_to = db.Column(db.String(50), nullable=True)


    approval_status = db.Column(db.String(30), nullable=False, default="Not Required")
    resolution = db.Column(db.Text, nullable=True)


    created_at = db.Column(db.DateTime, server_default=db.func.now())


# -----------------------------
# Auth decorators
# -----------------------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "username" not in session:
            flash("Please login first.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# -----------------------------
# Routes
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")


        user = USERS.get(username)
        if user and check_password_hash(user["password"], password):
            session.clear()
            session["username"] = username
            session["role"] = user["role"]
            session["department"] = user["department"]
            flash("Login successful.", "success")
            return redirect(url_for("index"))


        flash("Invalid username or password.", "danger")


    return render_template("login.html")




@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))




@app.route("/")
@login_required
def index():
    role = session.get("role")
    username = session.get("username")


    if role == "admin":
        tickets = Ticket.query.order_by(Ticket.id.desc()).all()
    elif role == "ict":
        tickets = Ticket.query.filter(
            (Ticket.assigned_to == username) | (Ticket.assigned_to.is_(None))
        ).order_by(Ticket.id.desc()).all()
    elif role == "procurement":
        tickets = Ticket.query.filter(Ticket.approval_status == "Pending").order_by(Ticket.id.desc()).all()
    elif role == "employee":
        tickets = Ticket.query.filter(Ticket.created_by == username).order_by(Ticket.id.desc()).all()
    else:
        tickets = []


    return render_template("index.html", tickets=tickets)




@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        department = request.form.get("department", session.get("department", "ICT")).strip()
        priority = request.form.get("priority", "Medium").strip()


        allowed_departments = ["ICT", "HR", "Finance", "Procurement"]
        allowed_priorities = ["Low", "Medium", "High"]


        if not title:
            flash("Title is required.", "danger")
            return render_template("create.html")


        if not description:
            flash("Description is required.", "danger")
            return render_template("create.html")


        if department not in allowed_departments:
            flash("Invalid department.", "danger")
            return render_template("create.html")


        if priority not in allowed_priorities:
            flash("Invalid priority.", "danger")
            return render_template("create.html")


        new_ticket = Ticket(
            title=title,
            description=description,
            department=department,
            priority=priority,
            status="Open",
            created_by=session["username"],
            assigned_to=None,
            approval_status="Not Required",
            resolution=""
        )


        try:
            db.session.add(new_ticket)
            db.session.commit()
            flash("Ticket created successfully.", "success")
            return redirect(url_for("index"))
        except Exception:
            db.session.rollback()
            flash("Could not save ticket. Try again.", "danger")


    return render_template("create.html")




@app.route("/ticket_action/<int:id>", methods=["POST"])
@login_required
def ticket_action(id):
    action = request.form.get("action")
    ticket = Ticket.query.get_or_404(id)
    role = session.get("role")
    username = session.get("username")


    if role == "ict":
        if action == "take":
            ticket.assigned_to = username
            ticket.status = "In Progress"
            db.session.commit()
            flash("Ticket assigned to you.", "success")


        elif action == "pending_approval":
            ticket.status = "Waiting Approval"
            ticket.approval_status = "Pending"
            db.session.commit()
            flash("Approval request sent to Procurement.", "success")


        elif action == "resolve":
            resolution = request.form.get("resolution", "").strip()
            if not resolution:
                flash("Resolution is required.", "danger")
                return redirect(url_for("index"))


            ticket.resolution = resolution
            ticket.status = "Resolved"
            db.session.commit()
            flash("Ticket marked resolved.", "success")


    elif role == "procurement":
        if action == "approve":
            ticket.approval_status = "Approved"
            ticket.status = "In Progress"
            db.session.commit()
            flash("Purchase approved.", "success")


        elif action == "reject":
            ticket.approval_status = "Rejected"
            ticket.status = "Open"
            db.session.commit()
            flash("Purchase rejected.", "warning")


    elif role == "employee":
        if action == "close":
            if ticket.status == "Resolved":
                ticket.status = "Closed"
                db.session.commit()
                flash("Ticket closed successfully.", "success")


    elif role == "admin":
        if action == "take":
            ticket.assigned_to = username
            ticket.status = "In Progress"
            db.session.commit()
            flash("Ticket assigned by admin.", "success")


    return redirect(url_for("index"))




if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)