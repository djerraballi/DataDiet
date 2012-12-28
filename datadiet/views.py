from pyramid.view import view_config, forbidden_view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from pyramid.session import UnencryptedCookieSessionFactoryConfig
import datetime
from pyramid.security import remember, forget
import MySQLdb as mysql

def process_date_added(creation_date):
    delta = datetime.datetime.now() - creation_date
    days_since = delta.days
    if days_since <= 1:
        hours_since = (delta.seconds/3600)
        if hours_since <= 1: 
            minutes_since = (delta.seconds/60)
        else: 
            minutes_since = None
    else:
        hours_since = None


    if hours_since != None:
        if minutes_since != None:
            if minutes_since < 1:
                return "Added less than a minute ago"
            else: 
                return "Added " + str(minutes_since) + ' minutes ago'
        else:
            return "Added " + str(hours_since) + ' hours ago'
    else:
        return "Added " + str(days_since) + ' days ago'


@view_config(route_name='home', renderer='templates/home.pt')
def home_view(request):
    #check if user is logged in
    username = request.cookies.get('username', 0)
    #get posts
    db = mysql.connect('localhost', 'root', '', 'data_diet')
    cur = db.cursor()
    cur.execute("""SELECT * FROM posts, postAggregates WHERE posts.post_id = postAggregates.post_id ORDER BY hotness""")
    preprocessed_posts=cur.fetchall()
    posts = [dict(title=row[1], body=row[2], hyperlink=row[3], username=row[4], since_added=process_date_added(row[5]), points=(row[9] -row[10]), comment_link="", total_comments=row[11] ) for row in preprocessed_posts]
    if username != 0:
        return {'posts':posts}
    else: 
        return {'posts':posts}

@view_config(route_name='register', renderer='templates/register.pt')
def register_screen(request):
    username = request.cookies.get('username', 0)
    if username!= 0:
        return {'project':'DataDiet'}
    else:
        return {'project':'DataDiet'}

@view_config(route_name='login', renderer='templates/login.pt')
def login(request):
    login_url = request.resource_url(request.context, 'login')
    referrer = request.url
    if referrer == login_url:
        referrer='/datadiet'
    came_from = request.params.get('came_from', referrer)
    message=''
    username=''
    password=''
    if 'form.submitted' in request.params:
        username = request.params['username']
        password = request.params['password']

        #validate user in database
        db = mysql.connect('localhost', 'root', '', 'data_diet')
        cur = db.cursor()
        cur.execute("""SELECT users.username FROM users WHERE username=%s AND password=md5(%s)""", (username, password))
        username_check = cur.fetchone()
        db.close()

        if username_check != None:
            username_check = username_check[0]
            if username==username_check:
                headers = remember(request, username, max_age=3600)
                return HTTPFound(location = came_from, headers = headers)
            message = 'Failed Login'
        else:
            message = 'Failed Login'

    return dict(message = message, url=request.application_url + '/login', came_from = came_from, username=username, password=password)

@view_config(route_name='cpost', renderer='templates/cpost.pt')
def create_post(request):
    username = request.cookies.get('username', 0)
    if username!= 0:
        return {'project':'DataDiet'}
    else :
        return {'project':'DataDiet'}

@view_config(route_name='test_add_post', renderer='templates/home.pt')
def create_user(request):
    username = request.cookies.get('username', 0)
    #obtain inputs from post on cpost screen
    if request.method == 'POST':
        
        title = request.POST.get('title')
        body = request.POST.get('body')
        hyperlink = request.POST.get('hyperlink')

        #form validation
        if body == '':
            body = None

        if title == '' or hyperlink == '':
            #failed input return
            return {'project':'DataDiet'}

        db = mysql.connect('localhost', 'root', '','data_diet')
        cur = db.cursor()
        cur.execute("""INSERT INTO posts (title, body, hyperlink, username, creation_date) values (%s, %s, %s, %s, NOW())""", (title, body, hyperlink, username))
        db.commit()
        db.close()
    return {'project':'DataDiet'}

@view_config(route_name='test_create_user')
def create_user(request):
    #obtain inputs from post on register screen
    if request.method == 'POST':
        #form validation
        username = request.POST.get('username')
        password = request.POST.get('password')
        repeated_password = request.POST.get('r-password')
        email = request.POST.get('email')
        #email validation
        if email=='':
            email = None
        db = mysql.connect('localhost', 'root', '','data_diet')
        #check for user, email in database
        cur=db.cursor()
        cur.execute("""SELECT username FROM users WHERE username=%s""", (username))
        user_check = cur.fetchone()
        cur=db.cursor()
        cur.execute("""SELECT email FROM users WHERE email=%s""", (email))
        email_check = cur.fetchone()
        if user_check == None and email_check == None:
        #add user if user, email does not exist already
            cur = db.cursor()
            cur.execute("""INSERT INTO users (username, password, email, creation_date) VALUES (%s, md5(%s), %s, NOW())""", (username, password, email))
            db.commit()
            db.close()
            response=request.response
            response.set_cookie('username', username, max_age=3600)
        if user_check != None:
            return Response('username already exists')
        if email_check != None:
            return Response('email already exists')
    #set cookie
    #redirect to different route
    return HTTPFound(location=('/datadiet'))
#logout

#add tag

#like/dislike a post

