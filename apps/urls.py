"""demo_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from .views import *  # noqa

urlpatterns = [
    path('plans/', PlanListView.as_view(), name='plans'),
    path('plans/create', PlanCreate.as_view(), name='plans-create'),
    path('plans/<int:plan_pk>/update', PlanUpdate.as_view(), name='plans-update'),
    path('plans/', PlanListView.as_view(), name='plans'),
    path('posts/', PostView.as_view(), name='posts'),
]
