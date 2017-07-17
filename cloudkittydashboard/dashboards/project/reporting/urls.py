from django.conf.urls import url

from cloudkittydashboard.dashboards.project.reporting import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
]
