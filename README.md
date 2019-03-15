# Introduction
This is by far the largest Python/Django project I undertook independently. The base idea behind this was this to be the product that would be what my own company was founded upon. As usual with many attempts of tech startups, failure to find funding eventually caused this to die off. Not without the backup plan to throw this up onto my GitHub if things turned south. With that in mind, a lot of code was written in the year I worked on this. Needless to say; there is a lot to cover.

## The Pitch
In recent years the freelance workforce has become a major factor in driving the success of the US and worldwide economies.  Freelancers enjoy the freedom and flexibility to do their best work by working on their own terms while companies have the ability to work with talented experts when they need them.

We founded InFlow in 2017 to solve a massive problem still facing the freelance workforce.  Every year 34% of freelancers do work for a client and are not paid for it. In addition to the freelancers who experience non-payment a large majority of the workforce struggles to get paid on time.

With that knowledge, we set on out a mission to help create a more prosperous, happy and fulfilled freelance workforce by providing the tools freelancers need to be successful in today’s economy.

## The Stack
* Python 3.6
* Django Web Framework
* HTML/CSS/JavaScript/jQuery
* AngularJS
* MySQL
* Amazon Web Services

In addition, many Python libraries were used that can be found in the requirements.txt file, installing these requires the running of the following command;

```
pip install -r requirements.txt
```

## About some of the Python libraries
We intended to use the Strip API in order to make monetary calls and Amazon Boto to have users upload their files to our Cloud Instances, intended this to be the storage for our workshare platform. Some of the libraries of note in regards to these are

```
pip install -Iv requests==2.18.4
pip install -Iv boto3==1.7.63
pip install -Iv botocore==1.10.63
pip install -Iv Django==2.0.2
pip install -Iv django-easy-pdf==0.1.1
pip install -Iv stripe==1.77.1
```

I don't see a problem in installing later versions, but at the time of that requirements.txt file, these were the versions being used.

# Important Information 
As usual with a Django project, the most important file can be found in the settings.py file, in this project, located in the "inflowhq" folder. The most important part of this being what database is used. This project was created using MySQL as the backend, but theoretically any backend Django supports out of the box can be used.

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mysql instance name',
        'USER': 'mysql user name',
        'PASSWORD': 'MySql Login password',
        'HOST': 'mysql host name',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}
```

Once the database is configured, Django needs to migrate to build the schema

```
python manage.py migrate
```

Finally, because the app utilizes Django's user login, this command is needed to create a superuser

```
python manage.py createsuperuser
```

Finally, the below command starts the develpoment surver

```
python manage.py runserver
```

# About the Django Site Structure
Due to how Django is designed to break things down into individual "apps," this project has several apps in mind, each one tasked to handle a specific piece of function;

* inflowco
* inflowdemo
* accounts
* contractsandprojects
* talktostripe

Descriptions for each app is detailed below.

## inflowco
The primary purpose is this app is to be the main entry point for the site. This app hosts public facing pages and handles some high level login functions such as using Google or LinkedIn to log the user in if the appropriate post data is found. Hosts some files Google wants to see to verify the correct app and some generic models that do not belong anywhere else.

### Models
Nothing too special in this app, just some base utility models.

#### Currency
This was kind of "for the kicks of it" but also because I imagined sooner or later freelancers in other countries will want to charge in a currency other than USD. I realized later on that stripe would probably handle this better, but this model was created very early on in the app development.

#### Country
Country where the user is based, has some basic information and a reference to the base currency that user will be charging in.

#### EmailSignup
Base object to collect emails from a signup page, was going to use this listing for future marketing purposes or to import into MailChimp when the time came.

### Unit Tests
Not much going on here but since we had sign up pages and views that acted differently from each other, it was prudent to at least have some tests laid down. I wanted to see if the master pages on the public facing pages worked as expected by reading the context data from the resposne and see if I can successfully log in and see pages that require the user to be logged in. Also tested posting to pages to see if the email sign up worked as I expect them to.

### mailchimp.py
This was a separate class I was using with the intention of talking to MailChimp, a third party marketing email vendor. We intended to build this out a little further, but all we managed to do with the time given was to post to a specific list once a user signed up on the site. Still, it shows a base level how we use the requests library.