from pyramid.view import view_config, forbidden_view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from pyramid.session import UnencryptedCookieSessionFactoryConfig
import datetime
from pyramid.security import remember, forget, authenticated_userid
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

def check_logged_in(request):
    username = authenticated_userid(request)
    if username != None:
        logged_in = 1
    else: 
        logged_in = 0
    return username, logged_in

def db_connect():
    return mysql.connect('mysql.server', 'polypatentpendin', 'Patent33!', 'polypatentpendin$data_diet')

def db_create_user(db, username, password, email):
    cur = db.cursor()
    cur.execute("""INSERT INTO users (username, password, email, creation_date) VALUES (%s, md5(%s), %s, NOW())""", (username, password, email))
    db.commit()
    cur = db.cursor()
    cur.execute("""INSERT INTO userAggregates (username, karma) VALUES (%s, 0)""", (username))
    db.commit()
    db.close()


def db_create_post(db, title, body, hyperlink, username, diettag):
    cur = db.cursor()
    cur.execute("""INSERT INTO posts (title, body, hyperlink, username, creation_date) values (%s, %s, %s, %s, NOW())""", (title, body, hyperlink, username))
    last_row_id = cur.lastrowid
    db.commit()
    cur = db.cursor()
    cur.execute("""SELECT creation_date FROM posts WHERE posts.post_id = %s """, last_row_id)
    date = cur.fetchone()[0]
    cur.execute("""INSERT INTO postAggregates (post_id, rating, hotness, total_likes, total_dislikes, total_comments) VALUES (%s, %s, LOG10(TIME_TO_SEC(%s)), %s, %s, %s)""", (last_row_id, 0, date, 0, 0, 0))
    db.commit()
    cur=db.cursor()
    cur.execute("""INSERT INTO postDietTag (post_id, diet_tag_name, reinforcements) VALUES (%s, %s, %s)""", (last_row_id, diettag, 1))
    db.commit()
    db.close()

def db_add_diet_tag(db, diettag):
    cur = db.cursor()
    db.close()

def db_add_content_tag(db, contenttag):
    cur = db.cursor()
    db.close()

def diet_tag_class(diettag):
    if diettag == "Carbohydrate":
        diet_class="label"
    elif diettag == "Protein":
        diet_class="label label-important"
    elif diettag == "Vegetable":
        diet_class="label label-success"
    elif diettag == "Sweet":
        diet_class = "label label-info"
    else: 
        diet_class = "label-inverse"
    return diet_class

def post_like(db, username, post_id, like_status):
    cur = db.cursor()
    cur.execute("""INSERT INTO userPostLikes (username, post_id, like_status) values (%s, %s, %s)""", (username, post_id, like_status))
    if like_status == 1:
        cur.execute("""UPDATE postAggregates SET postAggregates.total_likes = postAggregates.total_likes+1 WHERE postAggregates.post_id = %s""", (post_id))
        cur.execute("""UPDATE userAggregates SET userAggregates.karma = userAggregates.karma + 1 WHERE userAggregates.username = %s""", (username))
    else:
        cur.execute("""UPDATE postAggregates SET postAggregates.total_dislikes = postAggregates.total_dislikes+1 WHERE postAggregates.post_id = %s""", (post_id))
        cur.execute("""UPDATE userAggregates SET userAggregates.karma = userAggregates.karma-1 WHERE userAggregates.username = %s""", (username))
    
    cur.execute("""SELECT total_likes, total_dislikes FROM postAggregates WHERE postAggregates.post_id = %s""", (post_id))
    totals = cur.fetchone()
    total_likes = totals[0]
    total_dislikes = totals[1]
    if total_likes - total_dislikes <= 0:
        cur.execute("""UPDATE postAggregates SET postAggregates.rating=0 WHERE postAggregates.post_id = %s""", (post_id))
    else:
         cur.execute("""UPDATE postAggregates SET postAggregates.rating = LOG10(%s) + 1 WHERE postAggregates.post_id = %s""", ((total_likes-total_dislikes), post_id))
    
    cur.execute("""UPDATE postAggregates SET postAggregates.hotness = postAggregates.hotness + postAggregates.rating WHERE postAggregates.post_id = %s""", post_id)
    db.commit()

def db_add_comment_to_post(db, username, comment, post_id):
    cur = db.cursor()
    db.close()

def db_add_comment_to_comment(db, username, comment, post_id, level):
    cur=db.cursor()
    db.close()

@view_config(route_name='home_view', renderer='templates/home.pt')
def home_view(request):
    #get posts
    username, logged_in = check_logged_in(request)
    db = db_connect()
    cur = db.cursor()
    cur.execute("""SELECT * FROM posts, postAggregates WHERE posts.post_id = postAggregates.post_id ORDER BY postAggregates.hotness DESC""")
    preprocessed_posts=cur.fetchall()
    posts = [dict(post_id = row[0], title=row[1], body=row[2], hyperlink=row[3], username=row[4], since_added=process_date_added(row[5]), points=(row[9]-row[10]), comment_link="/comments/" + str(row[0]), total_comments=row[11]) for row in preprocessed_posts]
    for post in posts:
        cur.execute("""SELECT diet_tag_name, MAX(reinforcements) FROM postDietTag WHERE postDietTag.post_id = %s""", post['post_id'])
        diettag = cur.fetchone()[0]
        diet_class = diet_tag_class(diettag)
        post['diettag'] = diettag
        post['diet_class'] = diet_class
    return {'posts':posts, 'logged_in':logged_in, 'username':username}

@view_config(route_name='login', renderer='templates/login.pt')
def login(request):
    login_url = request.resource_url(request.context, 'login')
    referrer = request.url
    if referrer == login_url:
        referrer='/'
    came_from = request.params.get('came_from', referrer)
    message=''
    username=''
    password=''
    if 'form.submitted' in request.params:
        username = request.params['username']
        password = request.params['password']

        #validate user in database
        db = db_connect()
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
    logged_in=0
    return dict(message = message, url=request.application_url + '/login', came_from = came_from, username=username, logged_in=logged_in)

@view_config(route_name='logout', renderer='templates/login.pt')
def logout(request):
    headers = forget(request)

    logout_url = request.resource_url(request.context, 'logout')
    referrer = request.url
    if referrer == logout_url:
        referrer = '/'
    came_from = request.params.get('came_from', referrer)

    return HTTPFound(location=came_from, headers=headers)

@view_config(route_name='cpost', renderer='templates/cpost.pt')
def create_post(request):
    username, logged_in = check_logged_in(request)
    message=''
    title=''
    body=''
    hyperlink=''
    diettag='Carbohydrate'
    came_from = request.params.get('came_from', '/')
    
    if 'form.submitted' in request.params:
        title = request.params['title']
        body = request.params['body']
        hyperlink = request.params['hyperlink']
        diettag = request.params['DietTag']
        #form validation
        if body == '':
            body = None
        if title != '' and hyperlink != '':
            if '//' not in hyperlink:
                hyperlink = 'http://' + hyperlink
            if logged_in == 1:
                db = db_connect()
                db_create_post(db, title, body, hyperlink, username, diettag)
                return HTTPFound(location = came_from)
            else:
                message= 'You must be logged in'
        else:
            message = 'Failed Post Creation, hyperlink and title fields must not be blank'

    return dict(message = message, url=request.application_url + '/cpost', came_from = came_from, username=username, title= title, body= body, hyperlink=hyperlink, diettag=diettag, logged_in=logged_in)

@view_config(route_name='register', renderer='templates/register.pt')
def register_screen(request):
    login_url = request.resource_url(request.context, 'register')
    referrer = request.url
    if referrer == login_url:
        referrer='/'
    came_from = request.params.get('came_from', referrer)

    message=''
    username=''
    password=''
    r_password = ''
    email = ''

    if 'form.submitted' in request.params:
        username = request.params['username']
        password = request.params['password']
        r_password = request.params['r_password']
        email = request.params['email']
        #email validation
        db = db_connect()
        #usrecheck, email check
        cur=db.cursor()
        cur.execute("""SELECT username FROM users WHERE username=%s""", (username))
        user_check = cur.fetchone()
        cur=db.cursor()
        cur.execute("""SELECT email FROM users WHERE email=%s""", (email))
        email_check = cur.fetchone()
        if user_check == None and email_check == None and r_password == password:
        #add user if user, email does not exist already
            db_create_user(db, username, password, email)
            headers = remember(request, username, max_age=3600)
            return HTTPFound(location = came_from, headers = headers)
        if user_check != None: 
            message = 'Username Already Exists!'
        if email_check != None:
            message = 'Email Already Exists!'
        if password != r_password:
            message = 'Passwords do not match? Try again!'
    logged_in=0
    return dict(message = message, url=request.application_url + '/register', came_from = came_from, username=username, email=email, logged_in = logged_in)

@view_config(route_name='likes', renderer='templates/home.pt')
def post_liker(request):
    username, logged_in = check_logged_in(request)

    referrer = '/'
    came_from = request.params.get('came_from', referrer) 

    if logged_in == 0:
        return HTTPFound(location=came_from)
    else:    
        if 'post.liked' in request.params:
            like_status = 1
        elif 'post.disliked' in request.params:
            like_status=0
        
        post_id = request.params.get('post_id')

        db = db_connect()
        post_like(db, username, post_id, like_status)

    return HTTPFound(location = came_from)

@view_config(route_name='add_tag', renderer='templates/tag_editor.pt')
def tags(request):
    username, logged_in = check_logged_in(request)
    tag_url = request.resource_url(request.context, 'add_tag')
    came_from = request.params.get('came_from', tag_url)

    if logged_in == 0:
        return HTTPFound(location=came_from)
    else:
        #show add tag form diet tags/content tags
        return HTTPFound(location=came_from)

        


@view_config(route_name='comments', renderer='templates/comments.pt')
def comment_view(request):
    username, logged_in = check_logged_in(request)
    post_id = request.matchdict['post_id']
    message = ''
    comment=''
    #fetch the post
    db = db_connect()
    cur = db.cursor()
    cur.execute("""SELECT * FROM posts, postAggregates WHERE posts.post_id = postAggregates.post_id AND posts.post_id=%s""", post_id)
    row=cur.fetchone()
    post = dict(post_id = row[0], title=row[1], body=row[2], hyperlink=row[3], username=row[4], since_added=process_date_added(row[5]), points=(row[9]-row[10]), comment_link="", total_comments=row[11])
    cur.execute("""SELECT diet_tag_name, MAX(reinforcements) FROM postDietTag WHERE postDietTag.post_id = %s""", post['post_id'])
    diettag = cur.fetchone()[0]
    diet_class = diet_tag_class(diettag)
    post['diettag'] = diettag
    post['diet_class'] = diet_class

    
    #pass stuff for form
    comment_url = request.resource_url(request.context, 'comments')
    came_from = request.params.get('came_from', comment_url)

    #Get all comments, pass all necessary variables



    #form submission case
    if "form.submitted" in request.params:
        comment = request.params.get('comment')
        #add somehting to the db



    form_dict=dict(message = message, url=request.application_url + '/comments/' + str(post_id), came_from = came_from, comment=comment)
    return {'post':post, 'form_dict': form_dict, 'logged_in' : logged_in, 'username' : username }


#like/dislike a post

