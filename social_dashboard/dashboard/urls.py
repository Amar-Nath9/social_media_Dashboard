from django.urls import path,include
from . import views
from django.views.generic.base import RedirectView
# from threads_dashboard.views import threads_dashboard

urlpatterns = [
    
    path('', RedirectView.as_view(url='/login/', permanent=False)),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('facebook-login/', views.facebook_login1, name='facebook_login1'),
    path('facebook/callback/', views.facebook_callback, name='facebook_callback'),
    path('dashboard/', views.dashboard, name='facebook_dashboard'),
      

]
