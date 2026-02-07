from django.urls import path, re_path, include

from django.db.models import Model

from django.utils.module_loading import autodiscover_modules

from .views import DashminModelCreateView, DashminModelListView, DashminModelUpdateView

from .sites import register


class ModelDashmin:
    model = Model

    list_display = ['name']
    filters = []
    search_fields = []

    @classmethod
    def get_list_template(cls):
        return 'dashmin/[app_id]/[model_id]/index.html'

    @classmethod
    def get_update_template(cls):
        return 'dashmin/[app_id]/[model_id]/[node_id]/update.html'

    @classmethod
    def get_create_template(cls):
        return cls.get_update_template()

    @classmethod
    def get_queryset(cls):
        return cls.model.objects

    @classmethod
    def get_user_queryset(cls, user):
        """
        Limit the queryset for the particular logged in user
        """
        return cls.get_queryset(user)

    @classmethod
    def urlpatterns(cls):
        view_urlpatterns = [
            path('update', DashminModelUpdateView.as_view(model=cls.model, dashboard=cls)),
        ]
        return [
            path('', DashminModelListView.as_view(model=cls.model, dashboard=cls)),
            path('create', DashminModelCreateView.as_view(model=cls.model, dashboard=cls)),
            path('<str:pk>/', include(view_urlpatterns)),
        ]
