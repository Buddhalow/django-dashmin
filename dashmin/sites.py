from django.urls import path, include
from .views import DashminModelCreateView, DashminModelListView, DashminModelUpdateView

from .urls import urlpatterns


class DashminSite:
    pass


class DefaultDashminSite:
    pass


def register(model, dashboard):
    view_urlpatterns = [
        path('edit', DashminModelUpdateView.as_view(model=model, dashboard=dashboard)),
    ]

    index_urlpatterns = [
        path('<string:pk>', include(view_urlpatterns)),
        path('', DashminModelListView.as_view(model=model, dashboard=dashboard)),
        path('create', DashminModelCreateView.as_view(model=model, dashboard_class=dashboard))
    ]

    urlpatterns += [
        path(model.app_id + '/' + model.name, include(index_urlpatterns))
    ]


site = DefaultDashminSite()
