from django.apps import AppConfig
from django import template 

class PagesConfig(AppConfig):
    name = "pages"
    
class DashboardConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dashboard"

register = template.Library()

@register.filter
def map_attribute(queryset, attribute):
    return [getattr(obj, attribute, '') for obj in queryset]