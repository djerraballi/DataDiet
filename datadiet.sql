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
    insert into commentAggregates (comment_id, total_likes, total_dislikes, points) VALUES (NEW.comment_id, 0, 0, 0, 0);


/* diet tags */
INSERT INTO dietTags values('Carbohydrate');

INSERT INTO dietTags values('Protein');

INSERT INTO dietTags values('Vegetable');

INSERT INTO dietTags values('Sweet');
