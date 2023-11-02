from django import template
from utilities.constants import DOCUMENT_TYPES

register = template.Library()


@register.filter
def return_doc_type_str(value):
    try:
        return dict(DOCUMENT_TYPES).get(str(value))
    except:
        return dict(DOCUMENT_TYPES).get('1')
    return dict(DOCUMENT_TYPES).get('1')
