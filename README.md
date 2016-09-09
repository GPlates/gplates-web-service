# gplates-web
repository for demoing gplates web services with different languages

Some instructions to set up your own django server and make an app like the one in this repo

1. Install django

2. Navigate to the folder where you want to make your app

Enter the following commands 
3. django-admin startproject GWS

4. cd GWS

5. python manage.py startapp reconstructions

6. Open to GWS/urls.py, then add a statement to import include
and add a line to the url patterns list,
e.g. url(r'^reconstructions/', include('reconstructions.urls')),

Back in the terminal, check that the server runs by typing
7. python manage.py runserver


