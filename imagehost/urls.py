from django.urls import path
from . import views, auth_views

app_name = 'imagehost'

urlpatterns = [
    # Web interface
    path('', views.index, name='index'),
    path('gallery/', views.gallery, name='gallery'),

    # Authentication
    path('login/', auth_views.login_page, name='login_page'),
    path('register/', auth_views.register_page, name='register_page'),
    path('auth/login/', auth_views.login_user, name='login'),
    path('auth/register/', auth_views.register_user, name='register'),
    path('auth/logout/', auth_views.logout_user, name='logout'),
    path('profile/', auth_views.user_profile, name='profile'),

    # API endpoints
    path('api/upload/', views.upload_image, name='upload'),
    path('api/images/', views.list_images, name='list_images'),
    path('api/images/<int:image_id>/delete/', views.delete_image, name='delete_image'),

    # Image serving (with view count)
    path('i/<path:image_path>', views.serve_image, name='serve_image'),
]
