queries = ["" for i in range(0, 17)]

### 0. List all the users who have at least 1000 UpVotes.
### Output columns and order: Id, Reputation, CreationDate, DisplayName
### Order by Id ascending
queries[0] = """
select Id, Reputation, CreationDate,  DisplayName
from users
where upvotes >= 1000
order by Id asc;
"""

### 1. Write a query to find all Posts who satisfy one of the following conditions:
###        - the post title contains 'postgres' and the number of views is at least 50000
###        - the post title contains 'mongodb' and the number of views is at least 25000
### The match should be case insensitive
###
### Output columns: Id, Title, ViewCount
### Order by: Id ascending
queries[1] = """
select Id, Title, ViewCount
from Posts
where (title ilike '%postgres%' and viewcount >= 50000) or (title ilike '%mongodb%' and viewcount >= 25000)
order by Id asc;
"""

### 2. Count the number of the Badges for the user with DisplayName 'JHFB'.
###
### Output columns: Num_Badges
queries[2] = """
select count(*) as Num_Badges
from users inner join badges on users.id = badges.userid
where displayname like 'JHFB';
"""

### 3. Find the Users who have received a "Guru" badge, but not a "Curious" badge.
### Only report a user once even if they have received multiple badges with the above names.
###
### Hint: Use Except (set operation).
###
### Output columns: UserId
### Order by: UserId ascending
queries[3] = """
select UserId
from users 
join (select userid, name from badges) badges on users.id = badges.userid
where name like 'Guru'
except
select UserId
from users 
join (select userid, name from badges) badges on users.id = badges.userid
where name like 'Curious'
order by UserId;
"""

### 4. "Tags" field in Posts lists out the tags associated with the post in the format "<tag1><tag2>..<tagn>".
### Find the Posts with at least 4 tags, with one of the tags being sql-server-2008 (exact match).
### Hint: use "string_to_array" and "cardinality" functions.
### Output columns: Id, Title, Tags
### Order by Id
queries[4] = """
select Id, Title, Tags
from posts
where ('<sql-server-2008' = any(string_to_array(tags, '>'))) and (cardinality(string_to_array(tags, '>')) > 4)
order by id;
"""

### 5. SQL "with" clause can be used to simplify queries. It essentially allows
### specifying temporary tables to be used during the rest of the query. See Section
### 3.8.6 (6th Edition) for some examples.
###
### Write a query to find the name(s) of the user(s) with the largest number of badges. 
### We have provided a part of the query to build a temporary table.
###
### Output columns: Id, DisplayName, Num_Badges
### Order by Id ascending (there may be more than one answer)
queries[5] = """
with temp as (
        select Users.Id as id, DisplayName, count(*) as num_badges 
        from users join badges on (users.id = badges.userid)
        group by users.id, users.displayname
        )
select *
from temp
where num_badges = (select max(num_badges) from temp);
"""

### 6. "With" clauses can be chained together to simplify complex queries. 
###
### Write a query to associate with each user the number of posts they own as well as the
### number of badges they have received, assuming they have at least one post and
### one badge. We have provided a part of the query to build two temporary tables.
###
### Restrict the output to users with id less than 100.
###
### Output columns: Id, DisplayName, Num_Posts, Num_Badges
### Order by Id ascending
queries[6] = """
with temp1 as (
        select owneruserid, count(*) as num_posts
        from posts
        group by owneruserid),
temp2 as (
        select userid, count(*) as num_badges
        from badges
        group by userid) 
select userid as Id, DisplayName, num_posts as Num_Posts, num_badges as Num_Badges
from temp1 
join temp2 on temp1.owneruserid = temp2.userid
join users on temp2.userid = users.id
where userid < 100
order by Id;
"""

### 7. A problem with the above query is that it may not include users who have no posts or no badges.
### Use "left outer join" to include all users in the output.
###
### Feel free to modify the "with" clauses to simplify the query if you like.
###
### Output columns: Id, DisplayName, Num_Posts, Num_Badges
### Order by Id ascending
queries[7] = """
with temp1 as (
        select owneruserid, count(*) as num_posts
        from posts
        group by owneruserid),
temp2 as (
        select userid, count(*) as num_badges
        from badges
        group by userid)
select users.id as Id, users.displayname as DisplayName, 
        case when temp1.num_posts is NULL then 0 else temp1.num_posts end as Num_Posts,
        case when temp2.num_badges is NULL then 0 else temp2.num_badges end as Num_Badges
from users 
left outer join temp2 on users.id = temp2.userid
left outer join temp1 on users.id = temp1.owneruserid
where users.id < 100
order by Id;
"""

### 8. List the users who have made a post in 2009.
### Hint: Use "in".
###
### Output Columns: Id, DisplayName
### Order by Id ascending
queries[8] = """
with temp as (
        select owneruserid, creationdate
        from posts
        where extract(year from creationdate) in ('2009')  
)
select id, displayname
from users 
join temp on temp.owneruserid = users.id
order by Id;
"""

### 9. Find the users who have made a post in 2009 (between 1/1/2009 and 12/31/2009)
### and have received a badge in 2011 (between 1/1/2011 and 12/31/2011).
### Hint: Use "intersect" and "in".
###
### Output Columns: Id, DisplayName
### Order by Id ascending
queries[9] = """
with temp1 as (
        select owneruserid, creationdate
        from posts
        where extract(year from creationdate) in ('2009')  
),
temp2 as (
        select date, userid
        from badges
        where extract(year from date) in ('2011')  
),
temp3 as (
        select temp1.owneruserid as Id
        from temp1
        intersect
        select temp2.userid as Id
        from temp2
)
select temp3.Id, users.displayname
from temp3
join users on temp3.Id = users.id
order by Id;
"""

### 10. Write a query to output a list of posts with comments, such that PostType = 'Moderator nomination' 
### and the comment has score of at least 10. So there may be multiple rows with the same post
### in the output.
###
### This query requires joining three tables: Posts, Comments, and PostTypes.
###
### Output: Id (Posts), Title, Text (Comments)
### Order by: Id ascending
queries[10] = """
with temp2 as (
        select id, posttypeid, title
        from posts
        where posttypeid = 6
),
temp3 as (
        select postid, text, score
        from comments
        where score >= 10
)
select temp3.postid as Id, temp2.title, temp3.text
from temp2
join temp3 on temp2.id = temp3.postid
order by Id;
"""


### 11. For the users who have received at least 200 badges in total, find the
### number of badges they have received in each year. This can be used, e.g., to 
### create a plot of the number of badges received in each year for the most active users.
###
### There should be an entry for a user for every year in which badges were given out.
###
### We have provided some WITH clauses to help you get started. You may wish to 
### add more (or modify these).
###
### Output columns: Id, DisplayName, Year, Num_Badges
### Order by Id ascending, Year ascending
queries[11] = """
with years as (
        select distinct extract(year from date) as year 
        from badges),
     temp1 as (
        select id, displayname, year
        from users, years
        where id in (select userid from badges group by userid having count(*) >= 200)
     ),
     temp2 as (
        select userid, count(*) as num_badges
        from badges
        group by userid
        having count(*) >= 200
     )
select temp1.id, temp1.displayname, temp1.year, temp2.num_badges
from users 
join temp2 on temp2.userid = users.id
join temp1 on temp1.id = temp2.userid
where users.id = temp1.id
order by Id, Year;
"""
# with years as (
#         select distinct extract(year from date) as year 
#         from badges),
#      temp1 as (
#         select id, displayname, year
#         from users, years
#         where id in (select userid from badges group by userid having count(*) >= 200)
#      ),
#      temp3 as (
#         select temp1.id as id, extract(year from date) as year, count(*) as num_badges
#         from badges
#         join temp1 on badges.userid = temp1.id and temp1.year = extract(year from badges.date)
#         group by temp1.id, extract(year from date)
#      ),
#      temp4 as (
#         select id, displayname, extract(year from date) as year, sum(num_badges) as num_badges
#         from temp3
#         group by id, displayname, year
#      )
# select temp4.id, users.displayname, temp4.year, temp4.num_badges
# from temp4
# join users on temp4.id = users.id
# group by temp4.id, users.displayname, temp4.year, temp4.num_badges
# order by temp4.id, temp4.year;

### 12. Find the post(s) that took the longest to answer, i.e., the gap between its creation date
### and the creation date of the first answer to it (in number of days). Ignore the posts with no
### answers. Keep in mind that "AcceptedAnswerId" is the id of the post that was marked
### as the answer to the question -- joining on "parentid" is not the correct way to find the answer.
###
### Hint: Use with to create an appropriate table first.
###
### Output columns: Id, Title, Gap
queries[12] = """
with temp as (
        select acceptedanswerid, creationdate from posts
        ),
        temp3 as (
                select id, posts.creationdate
                from posts
                join temp on posts.id = temp.acceptedanswerid
        ),
        temp2 as (
                select posts.id, posts.title, (temp3.creationdate - posts.creationdate) as gap
                from posts 
                join temp3 on posts.acceptedanswerid = temp3.id
        )
select id, title, temp2.gap
from temp2
where temp2.gap = (select max(gap) as gap from temp2);
"""


### 13. Write a query to find the posts with at least 7 children, i.e., at
### least 7 other posts have that post as the parent
###
### Output columns: Id, Title
### Order by: Id ascending
queries[13] = """
with temp as (
        select parentid, title
        from posts 
        order by parentid
        ),
        temp2 as (
                select parentid, count(*) as num_posts
                from temp
                group by parentid
                order by num_posts desc
        ),
        temp3 as (
                select parentid, num_posts
                from temp2
                where num_posts >= 7
        )
select temp3.parentid as id, title
from temp3 
join posts on posts.id = temp3.parentid;
"""

### 14. Find posts such that, between the post and its children (i.e., answers
### to that post), there are a total of 100 or more votes
###
### HINT: Use "union all" to create an appropriate temp table using WITH
###
### Output columns: Id, Title
### Order by: Id ascending
queries[14] = """
with temp as (
        (select posts.id, count(*) as num_votes
        from posts 
        join votes on votes.postid = posts.id
        where parentid is NULL
        group by posts.id 
        order by posts.id )
        union all
        (select posts.parentid as id, count(*) as num_votes
        from posts 
        join votes on votes.postid = posts.id
        where parentid is not NULL
        group by posts.id 
        order by posts.id )
        order by id
        ),
        temp4 as (
                select id, sum(num_votes) as total_num_votes
                from temp
                group by id
        )
select temp4.id, posts.title
from posts 
join temp4 on posts.id = temp4.id
where total_num_votes > 99
order by temp4.id;
"""

### 15. Let's see if there is a correlation between the length of a post and the score it gets.
### We don't have posts in the database, so we will do this on title instead.
### Write a query to find the average score of posts for each of the following ranges of post title length:
### 0-9 (inclusive), 10-19, ...
###
### We will ignore the posts with no title.
###
### HINT: Use the "floor" function to create the ranges.
###
### Output columns: Range_Start, Range_End, Avg_Score
### Order by: Range ascending

# Score
queries[15] = """
with temp as (
        select id, score
        from posts
        group by id
        ),
        temp2 as (
               select id, length(title) as length
               from posts
               where length(title) > 0
               group by id
        ),
        temp3 as (
                select temp2.id, temp.score, length
                from temp join temp2 on temp.id = temp2.id
        ),
        temp4 as (
                select floor(temp3.length / 10)*10 as Range_Start, floor(temp3.length / 10)*10 + 9 as Range_End, avg(score) as avg_score
                from temp3
                group by temp3.length/10
        )
select *
from temp4
order by Range_Start;
"""


### 16. Write a query to generate a table: 
### (VoteTypeDescription, Day_of_Week, Num_Votes)
### where we count the number of votes corresponding to each combination
### of vote type and Day_of_Week (obtained by extract "dow" on CreationDate).
### So Day_of_Week will take values from 0 to 6 (Sunday to Saturday resp.)
###
### Don't worry if a particular combination of Description and Day of Week has 
### no votes -- there should be no row in the output for that combination.
###
### Output column order: VoteTypeDescription, Day_of_Week, Num_Votes
### Order by VoteTypeDescription asc, Day_of_Week asc
queries[16] = """
with temp1 as (
        select extract('dow' from creationdate) as day_of_week, id
        from votes
        group by creationdate, id
        ),
        temp2 as (
                select id, votes.votetypeid, creationdate, description
                from votes 
                join votetypes on votes.votetypeid = votetypes.votetypeid
        ),
        temp3 as (
                select votetypeid, description as VoteTypeDescription, day_of_week, count(*) as num_votes
                from temp2 
                join temp1 on temp1.id = temp2.id
                group by votetypeid, day_of_week, description
        )
select temp3.VoteTypeDescription, day_of_week, num_votes
from temp3
order by VoteTypeDescription, day_of_week;
"""
