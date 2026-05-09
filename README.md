# iahc profile builder

Welcome to iahc profile builder it's one of my first projects on github I hope you love it

# Environments 

Create a .env file and allow your frontned server there:

SECRET_KEY=
DEBUG=
ALLOWED_HOSTS=

# Downloading the python libs

execute pip install -r requirements.txt

# Execute

python manage.py makemigrations accounts
python manage.py migrate

# Running

python manage.py runserver
