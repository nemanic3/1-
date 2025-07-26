from django.urls import path
from .views import SignupView, MeView, UpdateProfileView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('me/', MeView.as_view(), name='me'),
    path('update-profile/', UpdateProfileView.as_view(), name='update-profile'),
]
