from selectable.base import ModelLookup
from selectable.registry import registry

from suppliers.models import Supplier


class SupplierLookup(ModelLookup):
    model = Supplier
    fields = ('name', 'company_id', 'is_active', 'is_hidden')
    search_fields = ('name__icontains', )

    # filters = {'is_active': True, 'is_hidden': False, }

registry.register(SupplierLookup)
