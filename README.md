# gplates-web
repository for demoing gplates web services with different languages

#### [This repo will be kept private to begin with - once it is ready for public consumption we will move it to the 'gplates' github account]

## Contents
- files for the django framework 
- examples of making requests to this server using python (ipython notebooks)
- examples of making requests to this server using R (tested in Rstudio)
- examples of making requests to this server using bash/GMT 
- folder containing a store of different reconstruction model files

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



