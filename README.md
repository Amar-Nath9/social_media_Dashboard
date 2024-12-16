# social_media_Dashboard

# Social Media Dashboard

## Overview
The Social Media Dashboard allows users to connect with Facebook and Threads APIs to manage social media posts from a custom desktop application. Users can post simultaneously to both platforms with a single click.

## Prerequisites
1. Create a developer account and an app using the following documentation:
   - Facebook: [Create an App](https://developers.facebook.com/docs/development/create-an-app/)
   - Threads: [Create an App for Threads API](https://developers.facebook.com/docs/development/create-an-app/threads-use-case/)

## Facebook API Settings
Set the following environment variables in your application:

```python
FACEBOOK_APP_ID = "<FACEBOOK_APP_ID>"
FACEBOOK_APP_SECRET = "<FACEBOOK_APP_SECRET>"
FACEBOOK_REDIRECT_URI = "<set a redirect URI that is configured in the app>"
```

## Threads API Settings
Set the following environment variables in your application:

```python
HREADS_APP_ID = "<THREADS_APP_ID>"
THREADS_APP_SECRET = "<THREADS_APP_SECRET>"
THREADS_REDIRECT_URI = "<set a redirect URI that is configured in the app>"
```
## Installation
Install the dependencies using the following command:

```sh
pip install -r requirements.txt

```
## Migrate
By run this command:
```sh
python manage.py migrate
```
## Running the Project
Start the Django server using the following command:

```sh
python manage.py runserver
```


## Registration and Login
Register with your user details.

Log in with your credentials.

Log in to Facebook once to connect to the dashboard.

# Usage
Once logged in, the dashboard will display and allow you to manage posts for both Facebook and Threads. You can post simultaneously to both platforms with a single click

