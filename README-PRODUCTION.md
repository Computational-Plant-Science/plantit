Setup
===================

## 1) Create db folder
By default, the database files are kept in a db folder. create this folder in the root of the directory:

```bash
mkdir db
```

## 2) Set Secret Keys
Keys can be generated with the following code:

`SECRET_KEY`:
```python
import random
key = ''.join(random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50))
print("SECRET_KEY: %s"%(key,))
```

`FIELD_ENCRYPTION_KEY`:
```python
import cryptography.fernet
key = cryptography.fernet.Fernet.generate_key()
print("FIELD_ENCRYPTION_KEY: %s"%(key))
```

## 3) Set API_URL
`django/plantit/settings_prod.py` requires requires the API_URL variable to be set. The API_URL is used by remote job (like the ones that run on an HPC) to communicate with the web app. This can usually be set the same as that used in settings_dev.py, but changing the domain name to match where the web app is hosted.

## 4) Set server_name
Set correct `server_name` in `config/ngnix/conf.d/local.conf`

If this is left to localhost nginx will send a 444 Error for
all traffic that does not come from the localhost host name.  

## 5) Build Front End
Install the required npm modules and build the front end code:
```bash
cd django/front_end
npm install
npm run build
```

## 6) Build Containers
To build containers from the docker images run:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build
```

## 7) Collect static files
Static files must be manually collected so that the nginx web server can serve them:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml run djangoapp ./manage.py collectstatic --no-input
```


## 8) Setup database
The production environment uses a separate database container from that of the the dev env. It must be manually setup by running:  

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml run djangoapp ./manage.py makemigrations
docker-compose -f docker-compose.yml -f docker-compose.prod.yml run djangoapp ./manage.py migrate
```

__NOTE:__ If previous migrations were created on the code base (such as by using the development setup then running the production setup) you will need to remove the already created migrations:

```bash
#This find is only required if you rand makemigrations in dev environment
find . -path "./django/**/migrations/*.py" -not -name "__init__.py" -delete
```

# Add admin user
To add a user to a newly setup system

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml run djangoapp ./manage.py createsuperuser
```

# Google analytics
Google are supported via VueAnalytics. It is automatically added to the
website by setting the VUE_APP_ANALYTICS_ID variable is set in django/front_end/.env.

__NOTE:__ the .env file should not be committed to the repository. These variables are do not work with ``npm run watch``

E.g.:


```
VUE_APP_ANALYTICS_ID=id_provided_by_google
```

# Sentry IO
Sentry IO is supported via the vue module for sentry. It is automatically added to the website by setting the VUE_APP_SENTRY_IO_KEY and VUE_APP_SENTRY_IO_PROJECT variables in django/front_end/.env.

__NOTE:__ the .env file should not be committed to the repository. These variables are do not work with ``npm run watch``


E.g.:

```
VUE_APP_SENTRY_IO_KEY=ddd3adfa...
VUE_APP_SENTRY_IO_PROJECT=12345...
```

# Running
The website can be run in production mode using a different docker-compose config:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```
