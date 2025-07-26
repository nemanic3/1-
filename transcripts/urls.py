from django.urls import path
from .views import TranscriptUploadView, TranscriptStatusView, TranscriptParsedView

urlpatterns = [
    path('<int:user_id>/', TranscriptUploadView.as_view(), name='transcript-upload'),
    path('status/<int:user_id>/', TranscriptStatusView.as_view(), name='transcript-status'),
    path('parsed/<int:user_id>/', TranscriptParsedView.as_view(), name='transcript-parsed'),
]
