from django.urls import re_path, include, path

from .views import DashminModelListView, DashminModelCreateView, DashminModelUpdateView, ModelCreateView, ModelListView, ModelUpdateView

node_urlpatterns = [
    path('edit/', ModelUpdateView.as_view(), name='model-update'),
]

model_urlpatterns = [
    path('', ModelListView.as_view(), name='model-list'),
    path('create/', ModelCreateView.as_view(), name='model-create'),
    path('<str:node_id>/', include(node_urlpatterns)),
]

urlpatterns = [
    path('<str:app_id>/<str:model_id>/', include(model_urlpatterns)),
]


def model_urlpatterns(app_id, model_id):
    return [
        path('', ModelListView.as_view(), kwargs={ 'app_id': app_id, 'model_id': model_id }, name='model-list'),
        path('create/', ModelCreateView.as_view(), kwargs={ 'app_id': app_id, 'model_id': model_id }, name='model-create'),
        path('<str:node_id>/', include(node_urlpatterns), kwargs={ 'app_id': app_id, 'model_id': model_id }, name='model-view'),
    ]
