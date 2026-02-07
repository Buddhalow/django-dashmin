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
