To implement my project I decided to create a webapp, since I could draw some lessons learnt from
using Flask and SQL to help users store and retrieve information about their list of friends. I
have adapted a few variable-related and stylistic aspects from "Finance." Yet, the functionality and
use of the website is completely different.

To implement my project, I created a templates folder and a static folder. The templates folder contains
the html pages that the users sees. The static folder constains the stylesheet and the favicon that shows
up on the website's tab. I also have 4 files outside of this folder. I have 'application.py', where I use
python and flask to increase the interactivity of my website. I have 'finance.db', where the information that
the user provides is stored. I have helpers.py, which is adapted from finance, where I have some functions
I use in application.py. And I have requirements.txt, which contains the modules that must be installed to run
the website.

To create my project I started out with finance. From there I built my own website. I first ensured that my
database (which I call "finance.db") contains two tables: one containing the users information and one containing
information for each friend that each user enters (called "transactions"). I added columns to these tables corresponding
to the information that each would store (e.g. username, first name, password, etc. for "users" and friend_name,
reachout_deadline, frequency, etc. for "transactions).

My first challenge was how to add a friend into the database so that it would show up on a list of "All Friends". To add a
friend, I used the route "/buy". When using the GET method, the user would see a form (on prebuy.html page). When using POST
method, I used a db.execute expression so that the information would be inserted into the "transactions" table. In my "/" route,
there is another db.execute expression that extracts the friend names for the current user and stores it in a pythonic variable,
which is passed to the index.html page. I use jinja to display these names, one by one, on index.html. Also, I create a column
called "reachout deadline", this column will enter data equal to the current time (and so I use the datetime library) plus the
frequency that the user chose. This will store the specific time of the reachout deadline .

My next challenge was how to create a list that would contain only the friends that the user forgot to reach out to. To do this,
I created the /toreachoutto route. Here, I made use of the datetime library so that python knows what time it's currently. Then
I used a db.execute statement to extract, from the transactions table, a list of friend names for which the current time is greater
than the reachout deadline. These are the friends that the user forgot to reach out to. I display these users in a list in a similar
fashion to how it was explained in the paragraph above.


My next challenge was to create a friend-specific page for each user. To do this, I created the /eachfriendinfo route. When using a
GET request, python reads the URL (I ensure that the friend id is present in the URL by specifying so in the href attribute of the <a>
element of the name of each friend) and parses the friend id (this is not a problem since friend id's are just numbers, and so I do not
intend to make them private). After this, I use a db.execute statement to extract information from the friend with that specific friend id.
I created a menu that displays this information using some bootstrap elements.

My next challenge was to allow the user to submit automatic emails to their friends when they have to reach out. Again, I made use of the
/eachfriendinfo route. When using a POST request in /eachfriendinfo, we're talking about sending emails. To send the email, I again need to
extract information from the specific friend. It was a little difficult that I could not obtain the friend_id from the URL. Instead I included
it in a hidden form, so that the user only has to click a button (and not enter anything). But still, one of the form elements had the value of
the friend id (to do this I only needed to use jinja).

My next challenge was to have popup notifications on the "All Friends" Page where the user could click on the names of the friends to go to
their friend-specific page. To do this, I used the "/" route. When using GET, I use a db.execute statement to get the names of all the friends
for which the current time is greater than their reachout deadline (much like mentioned before). Then, I use a jinja for loop to show a notification
(styled with boostrap) that displays a message for each of these friends.