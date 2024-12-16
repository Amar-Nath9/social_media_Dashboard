from django.shortcuts import render, redirect
import requests
from social_dashboard import settings
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from threads_dashboard.views import threads_dashboard



from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.shortcuts import render, redirect

def register_view(request):
    if request.method == 'POST':
        name = request.POST['name']
        username = request.POST['username']  # Add username field
        email = request.POST['email']
        # mobile = request.POST['mobile']
        password = request.POST['password']

        # Validation checks
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return redirect('register')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return redirect('register')
        # if User.objects.filter(username=mobile).exists():
        #     messages.error(request, 'Mobile number already registered.')
        #     return redirect('register')

        # Create user
        user = User.objects.create(
            username=username,  # Store the username
            email=email,
            first_name=name,
            password=make_password(password)  # Hash the password
        )
        # user.profile.mobile = mobile  # Save mobile number if you extend the user model
        user.save()
        
        messages.success(request, 'Registration successful! Please login.')
        return redirect('login')

    return render(request, 'register.html')


# Login view for authenticating users
def login_view(request):
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        print(username,password)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('facebook_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


# Facebook Login initiation
def facebook_login1(request):
    
    fb_login_url = (
        f"https://www.facebook.com/v15.0/dialog/oauth?"
        f"client_id={settings.FACEBOOK_APP_ID}"
        f"&redirect_uri={settings.FACEBOOK_REDIRECT_URI}"
        f"&state={request.session.session_key}"
        f"&scope=email,public_profile,pages_manage_posts"
    )
    return redirect(fb_login_url)


# Facebook Dashboard to display user posts and create new ones
def facebook_dashboard(request):
 
    access_token = request.session.get('facebook_access_token')
  
    if not access_token:
       
        return redirect('facebook_login1')

    profile_data = {}
    posts = []
    page_access_data={}
    
    # access_token = "EAAIdEc61cCABO1zpLgrwzmaIlqZCddcyIdtuiZBVyZAwvLCDWZAhYlZBz4A98t2lLaxWkaiy0BKaw4h1yJqyMCVO8UvyYSOH6Ky0zQaFo2yHZCimDdPbuHFNwwAB2kOr2uL4fWsb66cOyBvvZA9NkOkl8JKv0Yz8DLtLyhJwJQgcQR9O5zpZAdjqmm7tddTjH8qjdkkjZAJZBF"
    page_access_url = f"https://graph.facebook.com/v15.0/me?fields=accounts&access_token={access_token}"
    page_responce = requests.get(page_access_url)
    page_access_data = page_responce.json()
    page_access_token = page_access_data['accounts']['data'][0]['access_token']

    if 'error' in page_access_data:
            messages.error(request, 'Failed to fetch profile information from Facebook.')
            return render(request, 'error.html', {'message': page_access_data['error']['message']})

  

    try:
        # Fetch user profile information
        profile_url = f"https://graph.facebook.com/v15.0/me?fields=id,name,email&access_token={access_token}"
        profile_response = requests.get(profile_url)
        profile_data = profile_response.json()

        if 'error' in profile_data:
            messages.error(request, 'Failed to fetch profilepage information from Facebook.')
            return render(request, 'error.html', {'message': profile_data['error']['message']})

        # Fetch user posts
        posts_url = f"https://graph.facebook.com/v15.0/me/feed?access_token={page_access_token}&fields=message,created_time,comments.summary(true),likes.summary(true)"
        posts_response = requests.get(posts_url)
        posts_data = posts_response.json()

        if 'error' in posts_data:
            messages.error(request, 'Failed to fetch posts from Facebook.')
            return render(request, 'error.html', {'message': posts_data['error']['message']})

        posts = posts_data.get('data', [])
    

    except requests.RequestException as e:
        messages.error(request, f"An error occurred while fetching data from Facebook: {e}")

    context = {
        'page_access_token':page_access_token,
        'profile': profile_data,
        'posts': posts
    }



    # Handle comment reply
    if request.method == 'POST' and 'reply_message' in request.POST:
        comment_id = request.POST.get('comment_id')
        reply_message = request.POST.get('reply_message')

        if comment_id and reply_message:
            reply_url = f"https://graph.facebook.com/v15.0/{comment_id}/comments"
            payload = {'message': reply_message, 'access_token': access_token}
            try:
                reply_response = requests.post(reply_url, data=payload)
                reply_data = reply_response.json()

                if 'error' in reply_data:
                    messages.error(request, 'Failed to reply to comment.')
                else:
                    messages.success(request, 'Replied to comment successfully!')
                    return redirect('facebook_dashboard')
            except requests.RequestException as e:
                messages.error(request, f"An error occurred while replying to a comment: {e}")

        return {'profile': profile_data, 'posts': posts}

    return context

# OAuth callback for Facebook Login
def facebook_callback(request):
  
    code = request.GET.get('code')
    state = request.GET.get('state')

    if not code or not state:
        return render(request, 'error.html', {'message': 'Invalid OAuth callback parameters.'})

    token_url = (
        f"https://graph.facebook.com/v15.0/oauth/access_token"
        f"?client_id={settings.FACEBOOK_APP_ID}"
        f"&client_secret={settings.FACEBOOK_APP_SECRET}"
        f"&redirect_uri={settings.FACEBOOK_REDIRECT_URI}"
        f"&code={code}"
    )

    response = requests.get(token_url)
    data = response.json()

    access_token = data.get('access_token')
    if not access_token:
        return render(request, 'error.html', {'message': 'Failed to obtain access token from Facebook.'})

    # Store access token in session
    request.session['facebook_access_token'] = access_token
    return redirect('facebook_dashboard')


# Logout view
def logout_view(request):
    auth_logout(request)
    # request.session.flush()
    messages.success(request, 'You have been logged out.')
    return redirect('login')




def dashboard(request):
    
    try:
        # Get data from Facebook
        fb_data = facebook_dashboard(request)
       
        if not isinstance(fb_data, dict):  # Check if Facebook view returned a valid context
            return fb_data  # Handles redirects or errors from the Facebook view
    except Exception as e:
        print(f"Error fetching Facebook data: {e}")
        fb_data = {'facebook_error': 'Unable to fetch Facebook data.'}

    try:
        # Get data from Threads
        threads_data = threads_dashboard(request)
        
        if not isinstance(threads_data, dict):  # Check if Threads view returned a valid context
            return threads_data  # Handles redirects or errors from the Threads view
    except Exception as e:
        print(f"Error fetching Threads data: {e}")
        threads_data = {'threads_error': 'Unable to fetch Threads data.'}

    # Handle unified post creation
    if request.method == 'POST':
        message = request.POST.get('message')
        if message:  # Proceed if the message is not empty
            # Facebook Posting Logic
            fb_page_access_token = fb_data.get('page_access_token')
            
            if fb_page_access_token:
                try:
                    create_post_url = f"https://graph.facebook.com/v15.0/me/feed?message={message}&access_token={fb_page_access_token}"
                    create_post_response = requests.post(create_post_url)
                    post_data = create_post_response.json()

                    if 'error' in post_data:
                        messages.error(request, 'Failed to create post on Facebook.')
                    else:
                        messages.success(request, 'Post created successfully on Facebook!')
                except requests.RequestException as e:
                    messages.error(request, f"An error occurred while creating a post on Facebook: {e}")

            # Threads Posting Logic
            threads_access_token = request.session.get('threads_access_token')
            threads_profile_id = threads_data.get('threads_profile', {}).get('id')
            if threads_access_token and threads_profile_id:
                try:
                    # Step 1: Create Media Container
                    create_container_url = f"https://graph.threads.net/v1.0/{threads_profile_id}/threads"
                    container_payload = {
                        "media_type": "TEXT",
                        "text": message,
                        "access_token": threads_access_token,
                    }
                    container_response = requests.post(create_container_url, data=container_payload)
                    container_data = container_response.json()

                    if 'error' not in container_data:
                        creation_id = container_data['id']

                        # Step 2: Publish Media Container
                        publish_post_url = f"https://graph.threads.net/v1.0/{threads_profile_id}/threads_publish"
                        publish_payload = {
                            "creation_id": creation_id,
                            "access_token": threads_access_token,
                        }
                        publish_response = requests.post(publish_post_url, data=publish_payload)
                        publish_data = publish_response.json()

                        if 'error' not in publish_data:
                            messages.success(request, 'Post created successfully on Threads!')
                        else:
                            messages.warning(request, 'Failed to publish post on Threads.')
                    else:
                        messages.warning(request, 'Failed to create media container on Threads.')
                except requests.RequestException as e:
                    messages.error(request, f"An error occurred with Threads: {e}")

        return redirect('facebook_dashboard')

    # Merge data and render dashboard
    context = {**fb_data, **threads_data}  # Combine both dictionaries
    return render(request, 'dashboard.html', context)
