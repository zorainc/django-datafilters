try:
    from django.views.generic.base import ContextMixin as mixin_base
except ImportError:
    mixin_base = object

__all__ = ('FilterFormMixin',)


class FilterFormMixin(mixin_base):
    '''
    Mixin that adds filtering behaviour for list-based views.

    Requirements for view:
      * `get_queryset` is used to filter the queryset is this is used by
        the standard `ListView` to generate the queryset.
      * View must define `filter_form_cls` class attribute as a filtering
        form class to use (subclass of `datafilters.filterform.FilterForm`).

    New behaviour:
      * context will have a bound filterform as `filterform` (with `data`
        from `GET` parameters);
      * Queryset returned by the parent `get_queryset` will be
        filtered according to the filterform.
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
                **self.get_filter_form_kwargs(
                    data=self.request.GET,
                    runtime_context=self.get_runtime_context(),
                    use_filter_chaining=self.use_filter_chaining
                ))

    def get_context_data(self, **kwargs):
        kwargs.update(filterform=self.get_filter_form())
        return super(FilterFormMixin, self).get_context_data(**kwargs)

    def get_filter_form_kwargs(self, **kwargs):
        return kwargs

    def get_queryset(self):
        filter_form = self.get_filter_form()
        if not filter_form is None and filter_form.is_valid():
            return filter_form.filter(
                super(FilterFormMixin, self).get_queryset()
            ).distinct()
        return super(FilterFormMixin, self).get_queryset()

    def get_runtime_context(self):
        return {'user': self.request.user}
