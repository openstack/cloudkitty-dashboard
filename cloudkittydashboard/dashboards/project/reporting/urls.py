from django.urls import re_path

from cloudkittydashboard.dashboards.project.reporting import views

urlpatterns = [
    re_path(r'^$', views.IndexView.as_view(), name='index'),
]
