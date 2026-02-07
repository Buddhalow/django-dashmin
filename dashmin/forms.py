from django.forms import ModelForm

from django.db.models import Model


class DashboardModelForm(ModelForm):
    class Meta:
        model = Model

        fields = '__all__'
