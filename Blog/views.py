
from datetime import datetime
from sqlalchemy import desc

from flask import render_template, request, url_for, redirect, flash
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flaskext.markdown import Markdown

from Blog import app, db
from Blog.models import Post, User, Comment
from Blog.forms import LoginForm, RegisterForm


# use markdown to process the blog content
Markdown(app)

# set up the loginManage logic
app.secret_key = 'Blog'

loginManager = LoginManager(app)
loginManager.session_protection = "strong"
loginManager.login_view = "login"

# in this case, the user identifier is the username(must be unique)
@loginManager.user_loader
def loadUser(user_id):
    return User.query.filter_by(username=user_id).first()




# method to assist the display of 2 colmuns of categories
def GetCategory():
    result = list(db.session.query(Post.category).distinct())
    return result[int(len(result)/2):], result[:int(len(result)/2)] 

# index, home page
@app.route('/')
@app.route('/home')
def home():

    pageNo = 1
    posts = Post.query.join(User, User.id==Post.userid).add_columns(User.username, Post.id, Post.title, Post.timestamp, Post.body, Post.category).order_by(desc(Post.timestamp)).paginate(pageNo, 3, False).items
    
    categoryLeft, categoryRight = GetCategory()

    return render_template(
        'index.html',
        posts = posts,
        pageNo = pageNo,
        categoryLeft = categoryLeft,
        categoryRight = categoryRight,
        year=datetime.now().year
    )

# this is the view for ajax result generating
# using ajax to do the partial refresh of (previous/next list of posts)
@app.route('/renderPost', methods=['POST'])
def renderPost():

    action = request.form["action"]
    pageNo = request.form["pageNo"]


    if action == "previous":
        newPageNo = int(pageNo) + 1  
    elif action == "next":
        newPageNo = int(pageNo) - 1  
    else:
        newPageNo = 1
    
    if newPageNo < 1:
        newPageNo = 1

    posts = Post.query.outerjoin(User, User.id==Post.userid).add_columns(User.username, Post.id, Post.title, Post.timestamp, Post.body, Post.category).order_by(desc(Post.timestamp)).paginate(newPageNo, 3, False).items

    if (len(posts) == 0) and (newPageNo != 1):
        newPageNo = newPageNo - 1
        posts = Post.query.outerjoin(User, User.id==Post.userid).add_columns(User.username, Post.id, Post.title, Post.timestamp, Post.body, Post.category).order_by(desc(Post.timestamp)).paginate(newPageNo, 3, False).items

    return render_template('renderPost.html', posts = posts, pageNo = newPageNo, year=datetime.now().year)




# this is the serach function for title
@app.route('/search')
def search():
    categoryLeft, categoryRight = GetCategory()
    pageNumber = request.args.get("pageNumber", None)
    search = request.args.get("search", None)
    if pageNumber is None:
        pageNumber = 1
    else:
        pageNumber = int(pageNumber)

    paginate = Post.query.outerjoin(User, User.id==Post.userid).add_columns(User.username, Post.id, Post.title, Post.timestamp, Post.body, Post.category).filter(Post.title.like("%{}%".format(search))).order_by(desc(Post.timestamp)).paginate(pageNumber, 3, False)
    return render_template('search.html', search=search, paginate=paginate,categoryLeft = categoryLeft, categoryRight = categoryRight, year=datetime.now().year)



# this is the serach function for category
@app.route('/search/category/<category>')
def searchCategory(category):
    categoryLeft, categoryRight = GetCategory()
    pageNumber = request.args.get("pageNumber", None)
    if pageNumber is None:
        pageNumber = 1
    else:
        pageNumber = int(pageNumber)

    paginate = Post.query.outerjoin(User, User.id==Post.userid).add_columns(User.username, Post.id, Post.title, Post.timestamp, Post.body, Post.category).filter(Post.category == category).order_by(desc(Post.timestamp)).paginate(pageNumber, 3, False)
    return render_template('searchCategory.html', category=category, paginate=paginate, categoryLeft = categoryLeft, categoryRight = categoryRight, year=datetime.now().year)
    

# this is the serach function for author
@app.route('/search/author/<author>')
def searchAuthor(author):
    categoryLeft, categoryRight = GetCategory()
    pageNumber = request.args.get("pageNumber", None)
    if pageNumber is None:
        pageNumber = 1
    else:
        pageNumber = int(pageNumber)

    paginate = Post.query.outerjoin(User, User.id==Post.userid).add_columns(User.username, Post.id, Post.title, Post.timestamp, Post.body, Post.category).filter(User.username == author).order_by(desc(Post.timestamp)).paginate(pageNumber, 3, False)
    return render_template('searchAuthor.html', author=author, paginate=paginate, categoryLeft = categoryLeft, categoryRight = categoryRight, year=datetime.now().year)
    



# this is the view for showing a specific post
@app.route('/post/<postId>')
def showPost(postId):
    selectedPost=Post.query.outerjoin(User, User.id==Post.userid).add_columns(User.username, Post.id, Post.title, Post.timestamp, Post.body, Post.category).filter(Post.id == postId).first()
    Comments=Comment.query.outerjoin(User, User.id==Comment.userid).filter(Comment.postid == postId).add_columns(User.username, Comment.body, Comment.id, Comment.timestamp, Comment.postid).order_by(desc(Comment.timestamp)).all()

    categoryLeft, categoryRight = GetCategory()

    return render_template(
        'post.html',
        post = selectedPost, categoryLeft = categoryLeft,
        categoryRight = categoryRight,
        year=datetime.now().year,
        Comments = Comments
    )


# this is the view to handle the comments submitted
@app.route('/createComment', methods=['POST'])
@login_required
def createComment():
    comment = request.form["comment"]
    postId = request.form["postId"]

    newComment = Comment(body = comment
            ,userid = current_user.id
            ,postid = int(postId))
    db.session.add(newComment)
    db.session.commit()

    return redirect(url_for('showPost', year=datetime.now().year, postId = postId))



# this is the view for creating a new post, using the markdown format
@app.route('/submitPost', methods=['GET', 'POST'])
@login_required
def submitPost():
    if request.method == "GET":
        return render_template('submitPost.html', year=datetime.now().year)
    elif request.method == "POST":
        newPost = Post(title = request.form["title"],
                       userid = current_user.id,
                       category = request.form["category"],
                       body = request.form["content"])
        db.session.add(newPost)
        db.session.commit()
        return redirect(url_for('home'))






########################################################################################


# this is tha about page view
@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Flask Blog App'
    )

# this is the view for register
@app.route('/register', methods=['GET', 'POST'])
def register():
    registerForm = RegisterForm()
    if registerForm.validate_on_submit():
        newUser = User(username = registerForm.username.data
            ,password = registerForm.password.data)
        db.session.add(newUser)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template(
        'register.html',
        year=datetime.now().year,
        form = registerForm
    )


# this is the view for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    loginForm = LoginForm()
    if loginForm.validate_on_submit():
        user = User(username=loginForm.username.data, password=loginForm.password.data)
        dbUser = User.query.filter_by(username=loginForm.username.data).first()
        if (dbUser is None) or (loginForm.password.data != dbUser.password):
            return redirect(url_for('about'))
        else:
            login_user(user)
            return redirect(url_for('home'))

    return render_template(
        'login.html',
        year=datetime.now().year,
        form = loginForm
    )

# this is the view for logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))



