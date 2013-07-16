try:
    from django.views.generic.base import ContextMixin as mixin_base
except ImportError:
    mixin_base = object

__all__ = ('FilterFormMixin',)


class FilterFormMixin(mixin_base):
    '''
    Mixin that adds filtering behaviour for list-based views.

    Requirements for view:
      * `get_context_data` must receive a queryset to filter as a kwarg
        `object_list`. It is a default behaviour of standard `ListView`.
      * View must define `filter_form_cls` class attribute as a filtering
        form class to use (subclass of `datafilters.filterform.FilterForm`).

    New behaviour:
      * context will have a bound filterform as `filterform` (with `data`
        from `GET` parameters);
      * Queryset `object_list` will be filtered according to the filterform.
    '''

    filter_form_cls = None
    use_filter_chaining = False
    _filter_form = None

    def get_filter_form(self):
        if self._filter_form is None:
            self.init_filterform()
        return self._filter_form

    def init_filterform(self):
        if not self.filter_form_cls is None:
            self._filter_form = self.filter_form_cls(
                self.request.GET,
                runtime_context=self.get_runtime_context(),
                use_filter_chaining=self.use_filter_chaining)

    def get_context_data(self, **kwargs):
        context = kwargs

        context['filterform'] = f = self.get_filter_form()

        if not f is None and f.is_valid():
            queryset = context['object_list']
            context['object_list'] = f.filter(queryset).distinct()

        return super(FilterFormMixin, self).get_context_data(**kwargs)

    def get_runtime_context(self):
        return {'user': self.request.user}
