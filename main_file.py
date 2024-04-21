from flask import Flask, render_template, request, flash, redirect, url_for, g, make_response, session, send_file
import flask_sqlalchemy
from sqlalchemy import LargeBinary
import io
from test import today
import bcrypt

db = flask_sqlalchemy.SQLAlchemy()
db_name = "database.db"
app = Flask(__name__)
app.config['SECRET_KEY'] = 'YOUR SECRET_KEY'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_name}"
db.init_app(app)


class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    user_id = db.Column(db.Integer)
    short_des = db.Column(db.String(300))
    long_des = db.Column(db.String(1000))
    image = db.Column(LargeBinary)
    link = db.Column(db.String(400))
    date = db.Column(db.String())
    filename = db.Column(db.String(300))
    data = db.Column(LargeBinary)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25))
    email = db.Column(db.String(25))
    password = db.Column(db.String(25))


class Feed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    email = db.Column(db.String(55))
    title = db.Column(db.String())
    message = db.Column(db.String(300))


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    with app.app_context():
        full_data = Data.query.all()
    return render_template("home.html", datas=full_data)


@app.route('/view/<int:image_id>')
def view(image_id):
    with app.app_context():
        full_data = Data.query.all()
        users = User.query.all()
    return render_template("view.html", datas=full_data, img=image_id, users=users)


@app.route('/image/<int:image_id>')
def get_img(image_id):
    imgs = db.session.query(Data).get(image_id)
    if imgs:
        response = make_response(imgs.image)
        response.headers['Content-Type'] = 'image/jpeg'
        return response
    return '<h1>image not found</h1>'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = db.session.query(User).filter_by(email=email).first()
        # print(User.get_id(user))
        if user:
            if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                flash("login successful", category='success')
                flash(f"hi {user.name}")
                # login_user(user)
                session['id'] = user.id
                return redirect(url_for('home'))
            else:
                flash("incorrect password", category='error')
        else:
            flash("user does not exist!!", category='error')
            return redirect('register')

    return render_template("login.html")


@app.route('/register', methods=['GET', 'POST'])
def sing_up():
    if request.method == 'POST':
        name_en = request.form.get('name')
        email_en = request.form.get('email')
        password_en = request.form.get('password')
        user = db.session.query(User).filter_by(email=email_en).first()

        if user:
            flash("email is already registered..", category="error")
            return redirect(url_for('login'))
        else:
            if len(password_en) < 8:
                flash("password should be greater than 8", category='error')
            else:
                pass_g = bcrypt.hashpw(password_en.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                with app.app_context():
                    new_user = User(name=name_en, email=email_en, password=pass_g)
                    db.session.add(new_user)
                    db.session.commit()
                user = db.session.query(User).filter_by(email=email_en).first()
                session['id'] = user.id
                return redirect(url_for('home'))
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('id', None)
    flash("logout success ful", category="success")
    return redirect(url_for('login'))


@app.before_request
def before_request():
    g.id = 0
    if 'id' in session:
        g.id = session['id']


@app.route('/add', methods=['GET', 'POST'])
def add():
    if g.id:
        text = "Add Your Project "
        h = "add"
        title = request.form.get('title')
        short = request.form.get('short')
        long = request.form.get('big')
        img = request.files.get('image')
        link = request.form.get('link')
        user_id = session['id']
        date = today()
        file = request.files.get('file')
        check = db.session.query(Data).filter_by(title=title).first()
        if request.method == 'POST':
            if check:
                flash("title is exists try new ", category='error')
            else:
                with app.app_context():
                    new_pro = Data(title=title, short_des=short, long_des=long, image=img.read(), date=date, link=link, user_id=user_id, filename=file.filename, data=file.stream.read())
                    db.session.add(new_pro)
                    db.session.commit()
                flash("correct ", category='success')
                return redirect(url_for('home'))
        return render_template('add.html', title=h, head=text)
    else:
        return redirect(url_for('login'))


@app.route('/edit/<int:data_id>', methods=['GET', 'POST'])
def edit(data_id):
    if g.id:
        text = "Edit Your Project "
        h = "edit"
        title = request.form.get('title')
        short = request.form.get('short')
        long = request.form.get('big')
        img = request.files.get('image')
        link = request.form.get('link')
        file = request.files.get('file')
        # user_id = session['id']
        date = today()
        if request.method == 'POST':
            with app.app_context():
                data_u = db.session.execute(db.select(Data).where(Data.id == data_id)).scalar()
                if title:
                    data_u.title = title
                if short:
                    data_u.short_des = short
                if long:
                    data_u.long_des = long
                if img:
                    data_u.image = img.read()
                if img:
                    data_u.link = link
                if file:
                    data_u.filename = file.filename
                    data_u.data = file.stream.read()
                data_u.date = date

                db.session.commit()
            return render_template('home.html')
        return render_template('add.html', head=text, title=h)


@app.route('/delete/<int:id>')
def delete(id):
    data = db.get_or_404(Data, id)
    db.session.delete(data)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/my_projects")
def my_projects():
    x = session['id']
    with app.app_context():
        full_data = Data.query.all()
    return render_template('my_proj.html', user_id=x, datas=full_data)


@app.route("/feed/<int:id>", methods=['GET', 'POST'])
def feed(id):
    if request.method == 'POST':
        email = request.form.get('email')
        msg = request.form.get('message')
        with app.app_context():
            data_u = db.session.execute(db.select(Data).where(Data.id == id)).scalar()
        title = data_u.title
        user_id = data_u.user_id
        with app.app_context():
            new_pro = Feed(email=email, message=msg, user_id=user_id, title=title)
            db.session.add(new_pro)
            db.session.commit()
        return redirect(url_for('home'))

    return render_template('feedback.html')


@app.route("/feeds")
def feeds():
    with app.app_context():
        full_data = Feed.query.all()
    check = db.session.query(Feed).filter_by(user_id=g.id).first()
    return render_template("all_feeds.html", msgs=full_data, check=check)


@app.route("/download/<int:file_id>")
def download_file(file_id):
    file_data = Data.query.get_or_404(file_id)
    return send_file(io.BytesIO(file_data.data), download_name=file_data.filename, as_attachment=True, mimetype="application/zip")


if __name__ == "__main__":
    app.run(debug=True)
