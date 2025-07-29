from django.urls import path
from .views import (
    GeneralCoursesView,
    MajorCoursesView,
    TotalCreditView,
    GeneralCreditView,
    MajorCreditView,
    StatisticsCreditView,
    StatusCreditView
)

urlpatterns = [
    path('courses/general/<int:user_id>/', GeneralCoursesView.as_view(), name='general-courses'),
    path('courses/major/<int:user_id>/', MajorCoursesView.as_view(), name='major-courses'),
    path('credit/total/<int:user_id>/', TotalCreditView.as_view(), name='credit-total'),
    path('credit/general/<int:user_id>/', GeneralCreditView.as_view(), name='credit-general'),
    path('credit/major/<int:user_id>/', MajorCreditView.as_view(), name='credit-major'),
    path('credit/statistics/<int:user_id>/', StatisticsCreditView.as_view(), name='credit-statistics'),
    path('credit/status/<int:user_id>/', StatusCreditView.as_view(), name='credit-status'),
]
