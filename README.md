# ElasticBot

## Create tree-defined button menu for telegram bot

### Setup

1. ```git clone https://github.com/zub3r/ElasticBot.git```
1. ```cd ElasticBot/```
1. ```virtualenv env -p python3```
1. ```. env/bin/activate```
1. ```pip install -r requirements/base.txt```
1. ```touch project/settings/settings_local.py```
1. ```echo TELEGRAM_TOKEN = 'YOUR_TOKEN_HERE' > project/settings/settings_local.py```
1. ```./manage.py createsuperuser```
1. ```celery worker -A project -B -l info```
1. ```./manage.py runserver```

### Create your button (in browser)

1. Navigate to ```http://localhost:8000/admin``` with credentials that you provided on step ```./manage.py createsuperuser```
1. Open ```Bot Commands``` menu and click to ```Create Bot Command``` at top-right corner of page
1. Fill out the fields (__bold__ are required):
* Url - url that will receive request from your bot after all fields will be filled out (at this case child bot commands must not exist)
* __Method__ - request method
* Parent - parent menu button (then current command will appear in submenu of selected one)
* Message - will be sent to user when he will select this command

#### URL parameters
* Is header - if checked - will be included into request headers instead of url params string
* Name - human-readable name of parameter
* __key__ - key of url param/header
* value - constant value for the parameter. If empty - will be requested from user

#### POST parameters
* name, __key__, value same as in __URL parameters__
* regex - regex that value shoud match. e.g. ```^\d+$``` will accept only numeric values

Click ```Save``` button

In terminal:
```^C```
```celery -A project worker -B -l info```

Check out the bot
Answer for your request will be returned to user
