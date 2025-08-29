from django.urls import path
from . import views

app_name = 'myapiapp'

urlpatterns = [
    path('upload/', views.upload_file_view, name='upload'),
]