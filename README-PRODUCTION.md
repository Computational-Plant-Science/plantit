# Database setup
The production environment uses a separate database container from that
of the the dev env. It must be manually setup by running:  

```bash
docker-compose exec djangoapp ./manage.py makemigrations
docker-compose exec djangoapp ./manage.py migrate
```

If previous migrations were run on the code base (such as by using the development setup then running the production setup) you will need to remove the already created migrations:

```bash
#This find is only required if you rand makemigrations in dev environment
find . -path "./django/**/migrations/*.py" -not -name "__init__.py" -delete
```

# Add admin user
To add a user to a newly setup system

```bash
docker-compose exec djangoapp ./manage.py createsuperuser
```

# Collect static
Static files must be manually collected so that the nginx web server can serve them:
