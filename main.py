from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail
import math
import json

#json_file="config.json"
with open("config.json","r") as c:
    params = json.load(c)["params"]

# create the extension
db = SQLAlchemy()

local_server=True

app = Flask(__name__)
app.secret_key = 'super secret key'

app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-password']
)
mail=Mail(app)


if(local_server):
    # configure the SQLite database, relative to the app instance folder
    app.config["SQLALCHEMY_DATABASE_URI"] = params['local_uri']
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = params['prod_url']   #production server
# initialize the app with the extension
db.init_app(app)

#table name is class and whether the table name starts with capital letter ot not start class name with capital letter
class Contact(db.Model):
    """
   # variables-sno, name, phno, email, msg, date
    """
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=False, nullable=False)
    phno = db.Column(db.String, unique=False, nullable=False)
    email = db.Column(db.String, unique=False, nullable=False)
    msg = db.Column(db.String, unique=False, nullable=False)
    date = db.Column(db.String(12), nullable=True)


class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    tagline = db.Column(db.String(20), nullable=False)
    #img_file = db.Column(db.String(12), nullable=True)


@app.route("/")
def html_run():
    posts = Posts.query.filter_by().all()
    last=math.ceil(len(posts)/int(params['no_of_posts']))
    #[0:params['no_of_posts']]

    #pagination logic-first:prev=#,next++;middle:prev--,next++;last:prev--,next=#
    page=request.args.get('page')
    if(not str(page).isnumeric()):
        page=1
    page=int(page)
    posts=posts[(page-1)*int(params['no_of_posts']):(page-1)*int(params['no_of_posts'])+int(params['no_of_posts'])]
    if(page==1):
        prev="#"
        next="/?page="+str(page+1)
    elif(page==last):
        prev = "/?page=" + str(page - 1)
        next = "#"
    else:
        prev = "/?page=" + str(page - 1)
        next = "/?page=" + str(page + 1)


    return render_template("index.html",params=params,posts=posts,prev=prev,next=next)

@app.route("/dashbord", methods=["GET","POST"])
def dashbord():
    if('user' in session and session['user']== params['admin_user']):
        posts = Posts.query.all()
        return render_template('dashboard.html',params=params,posts=posts)
    if request.method=="POST":
        #REDIRECT TO ADMIN PANEL
        username=request.form.get('uname')
        userpass=request.form.get('pass')
        if(username==params['admin_user'] and userpass==params['admin_password']):
            # set the session variable
            session['user']=username
            posts=Posts.query.all()
            return render_template('dashboard.html',params=params,posts=posts)
    return render_template("login.html",params=params)

@app.route("/about")
def about():
    return render_template("about.html",params=params)


@app.route("/post/<string:post_slug>",methods=["GET"])
def post_route(post_slug):
    post=Posts.query.filter_by(slug=post_slug).first()
    print(post.date)
    return render_template("post.html",params=params,post=post)



@app.route ("/edit/<string:sno>/", methods=["GET","POST"])
def edit(sno):
    if('user' in session and session['user']== params['admin_user']):
        if(request.method)=="POST":
            box_title=request.form.get('title')
            tline=request.form.get('tline')
            slug=request.form.get('slug')
            content=request.form.get('content')
            date=datetime.now()
            # new post
            if sno=='0':
                post = Posts(title=box_title, slug=slug, content=content, tagline=tline, date=date)
                db.session.add(post)
                db.session.commit()
            #edit post
            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.title = box_title
                post.tagline = tline
                post.slug = slug
                post.content = content
                post.date = date
                db.session.commit()
                return redirect('/edit/' + sno)

        post = Posts.query.filter_by(sno=sno).first()

        return render_template("edit.html",params=params,post=post)

@app.route ("/logout")
def logout():
    session.pop('user')
    return redirect('/dashbord')

@app.route("/delete/<string:sno>",methods=["GET","POST"])
def delete(sno):
    if('user' in session and session['user']== params['admin_user']):
        post=Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect("/dashbord")


@app.route ("/contact", methods=["GET","POST"],)
def contact():
    # import REQUEST PACKAGE
    if (request.method=='POST'):
        """#add entry to the data base
     
         variables name in data base-sno, name, phno, email, msg, date
         no need to add sno in because it is auto incremented
        """

        entry=Contact(
        name=request.form.get('name'),
        email=request.form.get('email'),
        phno=request.form.get('phone'),
        msg=request.form.get('message'),
        date=datetime.now()

        )
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from Blog' +entry.name,
                          sender=entry.email,
                          recipients=[params['gmail-user']],
                          body=entry.msg+"\n"+entry.phno
                          )
    return render_template("contact.html",params=params)



app.run(debug=True)