from django.apps import apps
from django.db.models import Model
from django.views.generic import ListView, CreateView, UpdateView

from dateutil.parser import parse

from django.db.models import ForeignKey, ManyToManyField, IntegerField, FloatField, DateTimeField, DateField

class DashminViewMixin:
    model = None
    dashboard = None

    @classmethod
    def as_view(cls, model=None, dashboard=None, *args, **kwargs):
        cls.as_view(*args, **kwargs)

        cls.model = model
        cls.dashboard = dashboard


class DashminModelListView(DashminViewMixin, ListView):
    model: Model = Model

    def get_template_names(self):
        ret = super().get_template_names()
        ret.append(self.dashboard.get_list_template())
        return ret

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        filters = {}
        for fieldname in self.dashboard.filters:
            field_object, model, direct, m2m = model._meta.get_field_by_name(fieldname)
            if not m2m and direct and isinstance(field_object, ForeignKey):
                node_ids = self.request.GET.getlist(fieldname + '_id')
                node = model.objects.get(
                    id__in=node_ids
                )
                filters[fieldname + '__in'] = node
            elif not m2m and direct and isinstance(field_object, ManyToManyField):
                node_ids = self.request.GET.getlist(fieldname + '_id')
                nodes = model.objects.filter(
                    id__in=node_ids
                )
                filters[fieldname + '__in'] = nodes
            else:
                field_id = fieldname.split('__')[0]
                value = self.request.GET.get(fieldname)
                if isinstance(field_object, IntegerField):
                    filters[fieldname] = int(value)
                elif isinstance(field_object, FloatField):
                    filters[fieldname] = float(value)
                elif isinstance(field_object, DateTimeField):
                    filters[fieldname] = parse(value)
                elif isinstance(field_object, DateField):
                    filters[fieldname] = parse(value)

            queryset = queryset.filter(**filters)

        return queryset

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        ret['list_display'] = self.dashboard.list_display
        filters = self.dashboard.filters

        ret['filters'] = []

        for fieldname in filters:
            field_object, model, direct, m2m = model._meta.get_field_by_name(fieldname)
            queryset = []

            if not m2m and direct and isinstance(field_object, ForeignKey):
                node_ids = self.request.GET.getlist(fieldname + '_id')
                node = model.objects.get(
                    id__in=node_ids
                )
                ret[fieldname] = node

            elif not m2m and direct and isinstance(field_object, ManyToManyField):
                node_ids = self.request.GET.getlist(fieldname + '_id')
                nodes = model.objects.filter(
                    id__in=node_ids
                )
                queryset = model.objects.all()

            ret['filters'].append({
                'name': fieldname,
                'objects': list(queryset)
            })

        return ret


class DashminModelCreateView(DashminViewMixin, CreateView):
    model = Model

    def get_template_names(self):
        ret = super().get_template_names()
        ret.append(self.dashboard.get_create_template())
        return ret

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        return ret


class DashminModelUpdateView(DashminViewMixin, UpdateView):
    model = Model

    def get_template_names(self):
        ret = super().get_template_names()
        ret.append(self.dashboard.get_update_template())
        return ret

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        return ret


class ModelUpdateView(UpdateView):
    model = Model

    template_name = 'dashmin/[app_id]/[model_id]/[node_id]/update.html'

    def get_template_names(self):
        ret = super().get_template_names()
        ret.append(self.dashboard.get_create_template())
        return ret

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        return ret


class ModelCreateView(CreateView):
    model = Model
    template_name = 'dashmin/[app_id]/[model_id]/create.html'

    def get_template_names(self):
        ret = super().get_template_names()
        ret.append(self.dashboard.get_create_template())
        return ret

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        return ret


class ModelListView(ListView):
    list_filters = []
    list_display = ['name']

    model = Model
    template_name = 'dashmin/[app_id]/[model_id]/index.html'

    def get_user_queryset(self, queryset):
        return queryset

    def get_filter_queryset(self, queryset):
        return self.get_user_queryset(queryset)

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)

        app_id = self.kwargs.get('app_id')
        model_id = self.kwargs.get('model_id')
        self.model = apps.get_model(app_id, model_id)

        if hasattr(self.model, 'list_filters'):
            self.list_filters = getattr(self.model, 'list_filters')

        ret['list_display'] = self.list_display

        filters = []

        for fieldname in self.list_filters:
            field_object, model, direct, m2m = model._meta.get_field_by_name(fieldname)
            if not m2m and direct and isinstance(field_object, ForeignKey):
                queryset = self.get_filter_queryset(model.objects)
                node_ids = self.request.GET.getlist(fieldname + '_id')
                nodes = queryset.filter(
                    id__in=node_ids
                )
                queryset = self.get_filter_queryset(model.objects)
                filters.append({
                    'id': fieldname,
                    'objects': queryset,
                    'type': 'belongsTo',
                    'nodes': nodes
                })

            elif not m2m and direct and isinstance(field_object, ManyToManyField):
                node_ids = self.request.GET.getlist(fieldname + '_id')
                queryset = self.get_filter_queryset(model.objects)
                filters.append({
                    'id': fieldname,
                    'objects': queryset,
                    'type': 'm2m'
                })
            else:
                if isinstance(field_object, IntegerField):
                    filters.append({
                        'id': fieldname,
                        'type': 'int'
                    })
                elif isinstance(field_object, FloatField):
                    filters.append({
                        'id': fieldname,
                        'type': 'float'
                    })
                elif isinstance(field_object, DateTimeField):
                    filters.append({
                        'id': fieldname,
                        'type': 'datetime'
                    })
                elif isinstance(field_object, DateField):
                    filters.append({
                        'id': fieldname,
                        'type': 'date'
                    })

            ret['filters'] = filters

        return ret

    def get_queryset(self, *args, **kwargs):
        app_id = self.kwargs.get('app_id')
        model_id = self.kwargs.get('model_id')
        self.model = apps.get_model(app_id, model_id)

        self.list_filters = []
        if hasattr(self.model, 'list_filters'):
            self.list_filters = getattr(self.model, 'list_filters')

        queryset = super().get_queryset(*args, **kwargs)
        filters = {}
        for fieldname in self.list_filters:
            field_object, model, direct, m2m = model._meta.get_field_by_name(fieldname)
            if not m2m and direct and isinstance(field_object, ForeignKey):
                node_ids = self.request.GET.getlist(fieldname + '_id')
                node = model.objects.get(
                    id__in=node_ids
                )
                filters[fieldname + '__in'] = node
            elif not m2m and direct and isinstance(field_object, ManyToManyField):
                node_ids = self.request.GET.getlist(fieldname + '_id')
                nodes = model.objects.filter(
                    id__in=node_ids
                )
                filters[fieldname + '__in'] = nodes
            else:
                field_id = fieldname.split('__')[0]
                value = self.request.GET.get(fieldname)
                if isinstance(field_object, IntegerField):
                    filters[fieldname] = int(value)
                elif isinstance(field_object, FloatField):
                    filters[fieldname] = float(value)
                elif isinstance(field_object, DateTimeField):
                    filters[fieldname] = parse(value)
                elif isinstance(field_object, DateField):
                    filters[fieldname] = parse(value)

            queryset = queryset.filter(**filters)

        return queryset
