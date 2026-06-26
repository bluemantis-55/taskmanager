from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from models import (
    db,
    User,
    Task
)

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.secret_key = "secret_key"

db.init_app(app)


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        user = User(
            username=username,
            email=email,
            password=hashed_password
        )
        print("Пользователь сохраняется")
        db.session.add(user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(
            email=email
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            session["user_id"] = user.id

            return redirect("/profile")

    return render_template("login.html")


@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect("/login")

    user = User.query.get(
        session["user_id"]
    )

    return render_template(
        "profile.html",
        user=user
    )


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


@app.route("/tasks")
def tasks():

    if "user_id" not in session:
        return redirect("/login")

    search = request.args.get("search")

    if search:

        tasks = Task.query.filter(
            Task.title.contains(search),
            Task.user_id == session["user_id"]
        ).all()

    else:

        tasks = Task.query.filter_by(
            user_id=session["user_id"]
        ).all()

    return render_template(
        "tasks.html",
        tasks=tasks
    )


@app.route("/task/create", methods=["GET", "POST"])
def create_task():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        task = Task(
            title=request.form["title"],
            description=request.form["description"],
            user_id=session["user_id"]
        )

        db.session.add(task)
        db.session.commit()

        return redirect("/tasks")

    return render_template("create_task.html")


@app.route("/task/edit/<int:id>", methods=["GET", "POST"])
def edit_task(id):

    task = Task.query.get_or_404(id)

    if request.method == "POST":

        task.title = request.form["title"]
        task.description = request.form["description"]

        db.session.commit()

        return redirect("/tasks")

    return render_template(
        "edit_task.html",
        task=task
    )


@app.route("/task/delete/<int:id>")
def delete_task(id):

    task = Task.query.get_or_404(id)

    db.session.delete(task)

    db.session.commit()

    return redirect("/tasks")


@app.route("/task/status/<int:id>")
def change_status(id):

    task = Task.query.get_or_404(id)

    if task.status == "Новая":
        task.status = "В работе"

    elif task.status == "В работе":
        task.status = "Выполнена"

    else:
        task.status = "Новая"

    db.session.commit()

    return redirect("/tasks")


if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)