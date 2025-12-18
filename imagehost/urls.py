from django.urls import path
from . import views

app_name = 'imagehost'

urlpatterns = [
    # Web interface
    path('', views.index, name='index'),
    path('gallery/', views.gallery, name='gallery'),

    # API endpoints
    path('api/upload/', views.upload_image, name='upload'),
    path('api/images/', views.list_images, name='list_images'),
    path('api/images/<int:image_id>/delete/', views.delete_image, name='delete_image'),

    # Image serving (with view count)
    path('i/<path:image_path>', views.serve_image, name='serve_image'),
]
