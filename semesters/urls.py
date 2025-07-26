from django.urls import path
from .views import (
    SemesterCourseListView,
    SemesterDetailView,
    SemesterMissingRequiredView,
    SemesterFilteredView
)

urlpatterns = [
    path('courses/lists/<int:user_id>/', SemesterCourseListView.as_view(), name='semester-course-lists'),
    path('<str:semester>/courses/<int:user_id>/', SemesterDetailView.as_view(), name='semester-detail'),
    path('<str:semester>/courses/missing-required/<int:user_id>/', SemesterMissingRequiredView.as_view(), name='semester-missing-required'),
    path('<int:user_id>/', SemesterFilteredView.as_view(), name='semester-filtered'),
]
