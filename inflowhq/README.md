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