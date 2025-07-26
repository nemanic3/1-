from django.urls import path
from .views import GraduationAnalysisView

urlpatterns = [
    path('credit/status/<int:user_id>/', GraduationAnalysisView.as_view(), name='graduation-status'),
]
