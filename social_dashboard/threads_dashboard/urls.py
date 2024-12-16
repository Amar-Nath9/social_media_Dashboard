from django.urls import path
from .views import threads_login, threads_callback, threads_dashboard, error_page

urlpatterns = [
    path('login/', threads_login, name='threads_login'),
    path('callback/', threads_callback, name='threads_callback'),
    path('', threads_dashboard, name='threads_dashboard'),
    path('error/', error_page, name='error_page'),
]
