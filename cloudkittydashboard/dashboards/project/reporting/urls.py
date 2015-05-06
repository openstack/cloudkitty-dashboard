from django.conf.urls import patterns
from django.conf.urls import url

from cloudkittydashboard.dashboards.project.reporting import views

urlpatterns = patterns(
    '',
    url(r'^$', views.IndexView.as_view(), name='index'),
)
