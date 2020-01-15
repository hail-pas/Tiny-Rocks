from django import forms
from django.template import loader


class JsonWidgets(forms.Textarea):
    template_name = 'admin/json_field.html'

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return template

# admin 中替换 JSONField 默认组件
# admin.ModelAdmin.formfield_overrides = {
#     JSONField: {'widget': JsonWidgets},
# }
