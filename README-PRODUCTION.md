Setup
===================

## 1) Create db folder
By default, the database files are kept in a db folder. create this folder in the root of the directory:

```bash
mkdir db
```

## 2) Set Secret Keys
`django/plantit/settings_prod.py` requires the secret and foreign keys be set.

New keys can be generated using the following code:

__SECRET_KEY__:
```python
import random
key = ''.join(random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50))
print("SECRET_KEY: %s"%(key,))
```

__FIELD_ENCRYPTION_KEY__:
```python
import cryptography.fernet
key = cryptography.fernet.Fernet.generate_key()
print("FIELD_ENCRYPTION_KEY: %s"%(key))
```

## 3) Set API_URL
`django/plantit/settings_prod.py` requires requires the API_URL variable to be set. The API_URL is used by remote job (like the ones that run on an HPC) to communicate with the web app. This can usually be set the same as that used in settings_dev.py, but changing the domain name to match where the web app is hosted.

## 4) Build Front End
Install the required npm modules and build the front end code:
```bash
cd django/front_end
npm install
npm run build
```

## 5) Collect static files
Static files must be manually collected so that the nginx web server can serve them:
```bash
docker-compose -f docker-compose.yml -f compose-prod.yml run djangoapp ./manage.py collectstatic --no-input
```

## 6) Build Containers
To build containers from the docker images run:

```bash
docker-compose -f docker-compose.yml -f compose-prod.yml up
```

## 7) Setup database
The production environment uses a separate database container from that of the the dev env. It must be manually setup by running:  

```bash
docker-compose -f docker-compose.yml -f compose-prod.yml run djangoapp ./manage.py makemigrations
docker-compose -f docker-compose.yml -f compose-prod.yml run djangoapp ./manage.py migrate
```

__NOTE:__ If previous migrations were created on the code base (such as by using the development setup then running the production setup) you will need to remove the already created migrations:

```bash
#This find is only required if you rand makemigrations in dev environment
find . -path "./django/**/migrations/*.py" -not -name "__init__.py" -delete
```

# Add admin user
To add a user to a newly setup system

```bash
docker-compose -f docker-compose.yml -f compose-prod.yml run djangoapp ./manage.py createsuperuser
```


# Running
The website can be run in production mode using a different docker-compose config:

```bash
docker-compose -f docker-compose.yml -f compose-prod.yml up
```
