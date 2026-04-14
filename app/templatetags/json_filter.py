import json
from django.template import Library

register = Library()

@register.filter
def json(data):
    """
    Convierte un objeto Python a JSON para usar en JavaScript.
    """
    return json.dumps(data, default=str)
