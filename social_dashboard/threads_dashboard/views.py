from django.shortcuts import render, redirect
from social_dashboard import settings
from django.contrib import messages
import requests


# Threads Login initiation
def threads_login(request):
   
    # Login url with the threads api
    login_url = (
        f"https://threads.net/oauth/authorize?"
        f"client_id={settings.THREADS_APP_ID}&"
        f"redirect_uri={settings.THREADS_REDIRECT_URI}&"
        f"scope=threads_basic,threads_content_publish"
        # f"state={request.session.session_key}"
        # f"&response_type=code"
    )
    return redirect(login_url)

# to show thw errors
def error_page(request):
    return render(request, 'error.html')


# Threads OAuth callback
def threads_callback(request):
    
    code = request.GET.get('code')
    if not code:
        return render(request, 'error.html', {'message': 'Invalid OAuth callback parameters.'})

    # calback api to generate the access_token
    token_url = (
        f"https://graph.threads.net/oauth/access_token?"
        f"client_id={settings.THREADS_APP_ID}&"
        f"client_secret={settings.THREADS_APP_SECRET}&"
        f"grant_type=authorization_code"
        f"&redirect_uri={settings.THREADS_REDIRECT_URI}&"
        f"code={code}"
    )
    response = requests.post(token_url)
    data = response.json()
    access_token = data.get('access_token')
    
    if not access_token:
        return render(request, 'error.html', {'message': 'Failed to obtain access token from Threads.'})

    # Store the access token in the session
    request.session['threads_access_token'] = access_token
    return redirect('threads_dashboard')


# Threads Dashboard
def threads_dashboard(request):
    print("enter to the dashboard funtion")
    # adding a specific key from the session
    request.session['threads_access_token']='THAAHdK0EynrVBYlgwU1BUSFFnRGlTVDJ5eDNBdDNSWDdxZAHRSY0lOM2lGdEI2ZAkRxUWlCNUZAQeUtwOE04bmVqRFJlN1hqT01fX0FEUWltSGpWZA3h3WVNmY0tjQnE2d3k0UXd6UlJ5YjJGd3J5QzdPMkNWMkh1SkxYLVY4NEwwZA25mZAwZDZD'
    
    

    threads_access_token = request.session.get('threads_access_token')
    if not threads_access_token:
        return redirect('threads_login')
    print("threads: tocken!!",threads_access_token)
    try:
       

        # Fetch user profile
        profile_url = f"https://graph.threads.net/v1.0/me?fields=id,username,name,threads_profile_picture_url,threads_biography&access_token={threads_access_token}"
        profile_response = requests.get(profile_url)
       
        if profile_response.status_code != 200:
            return render(request, 'error.html', {'message': 'Failed to fetch profile data from Threads.'})
        profile_data = profile_response.json()
        
        if 'error' in profile_data:
            
            messages.error(request, profile_data['error'])
            return redirect('error_page')

        # Fetch user threads
        threads_url = f"https://graph.threads.net/v1.0/me/threads?fields=id,media_product_type,media_type,media_url,permalink,owner,username,text,timestamp,shortcode,thumbnail_url,children,is_quote_post&access_token={threads_access_token}"
        threads_response = requests.get(threads_url)
        
        threads = threads_response.json().get('data', [])
     

    except requests.RequestException as e:
        messages.error(request, f"An error occurred: {e}")
        return redirect('error_page')
    
    
    return { 'threads_profile': profile_data,
        'threads': threads,}
