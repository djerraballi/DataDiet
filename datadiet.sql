CREATE TABLE users (
   username    varchar(16) unique not null,
   password varchar(32) not null,
   email  varchar(256) unique,
   creation_date  datetime,
   last_login  datetime,
   primary key (username)) ENGINE=INNODB;

CREATE TABLE comments (
   comment_id integer unsigned not null auto_increment,
   comment  text,
   username  varchar(16),
   creation_date   datetime,
   level integer,
   primary key (comment_id),
   foreign key (username) references users(username)) ENGINE=INNODB;

CREATE TABLE posts (
   post_id    integer unsigned not null auto_increment,
   title  varchar(200) not null,
   body  text,
   hyperlink varchar(500),
   username varchar(16),
   creation_date datetime,
   primary key (post_id),
   foreign key (username) references users(username)) ENGINE=INNODB;

CREATE TABLE contentTags (
    tag_name varchar(50),
    primary key (tag_name)) ENGINE=INNODB;

CREATE TABLE dietTags (
    tag_name varchar(50),
    primary key (tag_name)) ENGINE=INNODB;

/* relationships */
CREATE TABLE userPreferences(
  username varchar(16),
  content_tag_name varchar(50),
  primary key(username, content_tag_name),
  foreign key(username) references users(username),
  foreign key(content_tag_name) references contentTags(tag_name)) ENGINE=INNODB;

CREATE TABLE postDietTag (
  post_id    integer unsigned not null,
  diet_tag_name       varchar(50),
  reinforcements integer,
  primary key (post_id, diet_tag_name),
  foreign key (post_id) references posts(post_id),
  foreign key (diet_tag_name) references dietTags(tag_name)) ENGINE=INNODB;

CREATE TABLE postContentTags (
  post_id       integer unsigned not null,
  content_tag_name    varchar(50),
  reinforcements integer,
  primary key (post_id,content_tag_name),
  foreign key (post_id) references posts(post_id),
  foreign key (content_tag_name) references contentTags(tag_name)) ENGINE=INNODB;

CREATE TABLE postComments (
  post_id integer unsigned not null,
  comment_id integer unsigned not null,
  primary key(post_id, comment_id),
  foreign key (post_id) references posts(post_id),
  foreign key (comment_id) references comments(comment_id)) ENGINE = INNODB;

CREATE TABLE commentToComment (
  comment_id_base integer unsigned not null,
  comment_id integer unsigned not null,
  post_id integer unsigned not null,
  primary key (comment_id),
  foreign key (comment_id_base) references comments(comment_id),
  foreign key (comment_id) references comments(comment_id),
  foreign key (post_id) references posts(post_id)) ENGINE = INNODB;

CREATE TABLE userPostLikes (
  username varchar(16),
  post_id integer unsigned NOT NULL,
  like_status boolean,
  primary key (username, post_id),
  foreign key (username) references users(username),
  foreign key (post_id) references posts(post_id)) ENGINE = INNODB;

CREATE TABLE userCommentLikes (
  username varchar(16), 
  comment_id integer unsigned NOT NULL,
  like_status boolean, 
  primary key (username, comment_id),
  foreign key (username) references users(username),
  foreign key (comment_id) references comments(comment_id)) ENGINE = INNODB;

/* aggregates - do i want to keep them in a seperate table*/

CREATE TABLE postAggregates ( 
  post_id integer unsigned NOT NULL,
  rating integer, 
  hotness integer, 
  total_likes integer, 
  total_dislikes integer,
  total_comments integer, 
  primary key (post_id),
  foreign key (post_id) references posts(post_id)) ENGINE = INNODB;

CREATE TABLE commentAggregates (
  comment_id integer unsigned NOT NULL, 
  total_likes integer, 
  total_dislikes integer, 
  points integer, 
  primary key (comment_id),
  foreign key (comment_id) references comments(comment_id)) ENGINE = INNODB;

CREATE TABLE userAggregates ( 
  username varchar(16),
  karma integer,
  primary key (username),
  foreign key (username) references users(username)) ENGINE = INNODB;

/* triggers */

CREATE TRIGGER userCreation AFTER INSERT ON users
  FOR EACH ROW
    insert into userAggregates (username, karma) VALUES (NEW.username, 0);

CREATE TRIGGER postCreation AFTER INSERT ON posts
  FOR EACH ROW
    insert into postAggregates (post_id, rating, hotness, total_likes, total_dislikes, total_comments) VALUES (NEW.post_id, 0, 0, 0, 0, 0);

CREATE TRIGGER commentCreation AFTER INSERT ON comments
  FOR EACH ROW
  BEGIN
    insert into commentAggregates (comment_id, total_likes, total_dislikes, points) VALUES (NEW.comment_id, 0, 0, 0, 0);

DELIMITER //
CREATE TRIGGER addPostLike AFTER INSERT on userPostLikes 
  FOR EACH ROW
  BEGIN
    IF ( NEW.like_status = True ) THEN
      BEGIN
        UPDATE data_diet.postAggregates SET postAggregates.total_likes = postAggregates.total_likes+1 WHERE NEW.post_id = postAggregates.post_id;
        UPDATE data_diet.userAggregates SET userAggregates.karma = userAggregates.karma+1 WHERE userAggregates.username IN (SELECT posts.username FROM posts WHERE NEW.post_id = posts.post_id);
      END;
    ELSE
      BEGIN
        UPDATE data_diet.postAggregates SET postAggregates.total_dislikes = postAggregates.total_dislikes+1 WHERE NEW.post_id = postAggregates.post_id;
        UPDATE data_diet.userAggregates SET userAggregates.karma = userAggregates.karma-1 WHERE userAggregates.username IN (SELECT posts.username FROM posts WHERE posts.post_id = NEW.post_id);
      END;
    END IF;
    BEGIN
      IF (postAggregates.total_likes - postAggregates.total_dislikes < 0) THEN
        BEGIN
          UPDATE data_diet.postAggregates SET postAggregates.rating=1 WHERE NEW.post_id = postAggregates.post_id;
        END;
      ELSE
        BEGIN
          UPDATE data_diet.postAggregates SET postAggregates.rating = LOG10(postAggregates.total_likes - postAggregates.total_dislikes) WHERE NEW.post_id = postAggregates.post_id;
        END;
      END IF;
    UPDATE data_diet.postAggregates SET postAggregates.hotness = postAggregates.rating + LOG10(TIMESTAMP(postAggregates.creation_date)) WHERE NEW.post_id = postAggregates.post_id;
    END;
  END;


DELIMITER //
CREATE TRIGGER addCommentLike AFTER INSERT on userCommentLikes 
  FOR EACH ROW
  BEGIN
    IF (NEW.like_status) THEN
    BEGIN
      UPDATE commentAggregates SET commentAggregates.total_likes = commentAggregates.total_likes+1 FROM data_diet.commentAggregates WHERE NEW.comment_id = postAggregates.comment_id;
      UPDATE userAggregates SET userAggregates.karma = userAggregates.karma+1 FROM data_diet.userAggregates WHERE userAggregates.username IN (SELECT comments.username FROM comments WHERE NEW.comment_id = comments.comment_id);
    END;
    ELSE
    BEGIN
      UPDATE commentAggregates SET commentAggregates.total_dislikes = commentAggregates.total_dislikes-1 FROM data_diet.commentAggregates WHERE NEW.comment_id = postAggregates.comment_id;
      UPDATE userAggregates SET userAggregates.karma = userAggregates.karma-1 FROM data_diet.userAggregates WHERE userAggregates.username IN (SELECT comments.username FROM comments WHERE NEW.comment_id = comments.comment_id);
    END:
    END IF;
    UPDATE commentAggrets SET commentAggregates.points = commentAggregates.total_likes - commentAggregates.totaldislikes FROM data_diet.commentAggregates WHERE NEW.comment_id = postAggregates.comment_id;

  END;




/*Common Queries */

/*Sign up*/
INSERT INTO users (username, password, email, creation_date) values ('passed_username', md5('passeD_password'), 'passed_email', NOW());
INSERT INTO userAggregates values ('passed_username', 0);
/*login */
SELECT username
FROM users
WHERE username = ('passed_username') AND password = md5('passed_password')
/*create profile NOT YET IMPLEMENTED */

/*edit profile NOT YET IMPLEMENTED*/

/* post content*/
INSERT INTO posts (title, body, hyperlink, username, creation_date) values('passed_title', 'passed_body', 'passed_link', 'passed_username', NOW() );

/* create comment to POST */
INSERT into comments ('passed_comment', 'username', NOW();, 'passed_level')
INSERT into postComments ('passed_post_id', 'passed_comment_id')
/* create comment on comment */
INSERT into comments ('passed_comment', 'username', NOW();, 'passed_level')
INSERT into commentToComment('passed_comment_id_base', 'passed_comment_id', 'passed_post_id' )


/*add content tag to post */
/*if first add of tag_name in site*/
INSERT into contentTags (tag_name) values ('passed_content_tag_name')
/*if first add of tag_name to this post*/
INSERT into postContentTags (post_id, content_tag_name, reinforcements) values('passed_post_id', 'passed_content_tag_name', '1')
/*else if not first add of tag_name to this post*/
UPDATE postContentTags SET reinforcements = reinforcements + 1 WHERE post_id = ('passed_post_id') and tag_name = ('passed_content_tag_name')

/*add diet tag to post */
/*if first add of tag_name to this post*/
INSERT into postDietTags (post_id, diet_tag_name, reinforcements) values('passed_post_id', 'passed_diet_tag_name', '1')
/*else if not first add of tag_name to this post*/
UPDATE postDietTags SET reinforcements = reinforcements + 1 WHERE post_id = ('passed_post_id') and tag_name = ('passed_diet_tag_name')

/*add like/dislike to post*/
INSERT INTO userPostLikes (username, post_id, like_status) values ('passed_username', 'passed_post_id', 'passed_like_status')

/*add like/dislike to comment*/
INSERT INTO userPostLikes (username, comment_id, like_status) values ('passed_username', 'passed_comment_id', 'passed_like_status')



/*display hottest items*/
SELECT *
FROM posts, postAggregates
WHERE posts.post_id = postAggregates.post_id
ORDER BY hotness
/*display highest rated items*/
SELECT *
FROM posts, postAggregates
WHERE posts.post_id = postAggregates.post_id
ORDER BY rating
/*display most recent items*/
SELECT *
FROM posts, postAggregates
WHERE posts.post_id = postAggregates.post_id
ORDER BY creation_date DESC
/*Keyword Search: Title, Sort: hottest*/
SELECT *
FROM posts, postAggregates
WHERE posts.post_id = postAggregates.post_id AND post.title LIKE '%keyword%'
ORDER BY hotness
/*Keyword Search: Title, Sort: rating*/
SELECT *
FROM posts, postAggregates
WHERE posts.post_id = postAggregates.post_id AND post.title LIKE '%keyword%'
ORDER BY rating
/*Keyword Search: Title, Sort: recency*/
SELECT *
FROM posts, postAggregates
WHERE posts.post_id = postAggregates.post_id AND post.title LIKE '%keyword%'
ORDER BY creation_date DESC
/*Keyword Search: Tags Sort: hottest*/
SELECT *
FROM posts, postAggregates, postContentTags
WHERE posts.post_id = postAggregates.post_id AND posts.post_id = postContentTags.post_id AND postContentTags.tag_name = 'keyword'
ORDER BY hotness
/*Keyword Search: Tags Sort: rating*/
SELECT *
FROM posts, postAggregates, postContentTags
WHERE posts.post_id = postAggregates.post_id AND posts.post_id = postContentTags.post_id AND postContentTags.tag_name = 'keyword'
ORDER BY rating
/*Keyword Search: Tags Sort: recency*/
SELECT *
FROM posts, postAggregates, postContentTags
WHERE posts.post_id = postAggregates.post_id AND posts.post_id = postContentTags.post_id AND postContentTags.tag_name = 'keyword'
ORDER BY creation_date DESC


/*display all items posted by the user*/
SELECT *
FROM users, posts, postAggregates
WHERE users.username = posts.username AND users.username = 'passed_username'




/* sample data */
/*sample users */
INSERT INTO users (username, password, email, creation_date) values ('derrab01', md5('password'), 'dj.erraballi@gmail.com', NOW());

INSERT INTO users (username, password, email, creation_date) values ('dj.sam', md5('password1'), 'crazydj123@gmail.com', NOW());

INSERT INTO users (username, password, email, creation_date) values ('djdragon', md5('protein'), 'derrab01@students.poly.edu', NOW());

INSERT INTO users (username, password, email, creation_date) values ('patentpending', md5('omnipotent'), 'polypatentpending@gmail.com', NOW());

INSERT INTO users (username, password, email, creation_date) values ('derrab02', md5('password'), NULL, NOW());

INSERT INTO users (username, password, email, creation_date) values ('derrab03', md5('password'), NULL , NOW());

/*sample posts */
INSERT INTO posts (title, body, hyperlink, username, creation_date) values('How to play guitar', 'This article has changed my life. Go read it. NOW!!!!', 'http://www.wikihow.com/Play-Guitar', 'derrab01', NOW() );

INSERT INTO posts (title, body, hyperlink, username, creation_date) values('How to live a little', 'This article has changed my life. Go read it. NOW!!!!', 'http://www.wikihow.com/life', 'djdragon', NOW() );

INSERT INTO posts (title, body, hyperlink, username, creation_date) values('How to play guitar', 'This article has changed my life. Go read it. NOW!!!!', 'http://www.wikihow.com/Play-Guitar', 'dj.sam', NOW() );

INSERT INTO posts (title, body, hyperlink, username, creation_date) values('How to play guitar', 'This article has changed my life. Go read it. NOW!!!!', 'http://www.wikihow.com/Play-Guitar', 'derrab02', NOW() );

INSERT INTO posts (title, body, hyperlink, username, creation_date) values('Bombing in London', '1000s Dead', 'http://www.wallstreetJournal.com', 'derrab01', NOW() );

/*sample comments*/

/* diet tags */
INSERT INTO dietTags values('Carbohydrate');

INSERT INTO dietTags values('Protein');

INSERT INTO dietTags values('Vegetable');

INSERT INTO dietTags values('Sweet');


/*content tags */
INSERT INTO contentTags values('Film');
INSERT INTO contentTags values('World News');
INSERT INTO contentTags values('Science');
INSERT INTO contentTags values('Computer Engineering');


/*Insert Post Likes*/

INSERT INTO userPostLikes values('derrab01', 2, True);
INSERT INTO userPostLikes values('djdragon', 2, True);
INSERT INTO userPostLikes values('derrab02', 2, True);
INSERT INTO userPostLikes values('derrab03', 2, True);

INSERT INTO userPostLikes values('derrab01', 3, False);
INSERT INTO userPostLikes values('djdragon', 3, True);
INSERT INTO userPostLikes values('derrab02', 3, False);
INSERT INTO userPostLikes values('derrab03', 3, False);