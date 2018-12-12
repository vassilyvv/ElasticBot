from django.urls import path
from project.api import views as api_views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = [
    path('approved_images/', api_views.ApprovedImages.as_view())
]
