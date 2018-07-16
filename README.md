# gplates-web
repository for demoing gplates web services with different languages


## Contents
- files for the django framework  
- folder containing a store of different reconstruction model files

- examples of accessing the service from different languages (R,matlab,bash/GMT,python) have now been moved to https://github.com/siwill22/gws-examples

## Notes on django setup
Some instructions to set up your own django server and make an app like the one in this repo

- Install django

- Navigate to the folder where you want to make your app

Enter the following commands 

- django-admin startproject GWS

- cd GWS

- python manage.py startapp reconstructions

- Open to GWS/urls.py, then add a statement to import include
and add a line to the url patterns list, 

    e.g. url(r'^reconstructions/', include('reconstructions.urls')),

Back in the terminal, check that the server runs by typing

- python manage.py runserver
- [TODO also necessary to run 'python manage.py migrate' at this point?]



