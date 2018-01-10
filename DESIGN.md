# we also need to write comments throughout application.py and clean up application.py

We based the front end of our project on an HTML/CSS template that we found online,
which was created by "Creative Tim." (https://www.creative-tim.com/) and
(https://www.creative-tim.com/product/light-bootstrap-dashboard). The template included
some HTML templates that we mostly wrote over, with the expection of the side bar, header,
and footer, as well as CSS and bootstrap components. We rearranged the folders to create a
static folder and changed the folder directories accordingly within the HTML templates.
We created a layout.html document that includes the sidebar, header, and footer, and
then used Jinja to extend this to each of the other documents. We decided to extend the
primary sidebar, header, and footer to each document so that all pages could be accessed
from every other page, and to make the HTML code for each individual page simpler.

The overall front-end design of OneCampus is as follows: The user enters the site through
a login page or the register page if they are a new user. The homepage is the dashboard,
which can be accessed from both "/" and "/dashboard." On the dashboard and on every other
page, there is a sidebar with links to each of the other pages, including addevent.html,
becomeadmin.html, createclub.html, editclub.html, events.html, findclubs.html, user.html,
and notifications.html. In addition, there is a profile.html page for each user id and a
club.html page for each club id that can only be accessed by clicking the name of the
specific user or specific club.

We have two python files that control our web application on the back end of our project:
helpers.py and application.py. helpers.py makes sure that users are logged in and handles user
errors by returning an apology. Application.py controls which html pages are returned to the
web app depending on what the user clicks on the front end, and controls what happens when
each button is clicked on a page. Much of the code in application.py is related to the
phpliteadmin databases, as each time a page is loaded, application.py queries one or more
tables to display the user's information, from a list of clubs to information about a specific
club. We decided to rely on tables in a database to organize and store our data, because we
have a lot of informationabout clubs, users, and events that is displayed on different parts
of our website.

In order to organize information about our users, clubs, and databases, we relied on 6
tables within our database.db, which are admins, clubs, events, users, userClubs, and
userEvents.Upon registration, a user gets added to the users table and is given a specific id.
Upon creation, a club gets added to the clubs table and is given a specific id. Likewise,
events are also added to the events table upon creation and given a specific id. The admins
table matches a clubId with the userId that is an admin for it, such that application.py can
check in the admins table to see what clubs a specific user is allowed to edit and create events
for. Similarly, the userClubs and userEvents tables associate specific user ids with club ids
and event ids so that we can keep track of what events a user is going to and what clubs a user
|has joined.