from django.views.generic.list import MultipleObjectMixin

__all__ = ('FilterFormMixin',)


class FilterFormMixin(MultipleObjectMixin):
    '''
    Mixin that adds filtering behaviour for list-based views.

    Requirements for view:
      * `get_queryset` is used to filter the queryset is this is used by
        the standard `ListView` to generate the queryset.
      * View must define `filter_form_cls` class attribute as a filtering
        form class to use (subclass of `datafilters.filterform.FilterForm`).

    New behaviour:
      * context will have a bound filterform as `filterform` (with `data`
        from `GET` parameters) or the name as defined in
        `context_filterform_name`.
      * Queryset returned by the parent `get_queryset` will be
        filtered according to the filterform.
    '''

    _filter_form = None
    filter_form_cls = None
    use_filter_chaining = False
    context_filterform_name = 'filterform'
    filter_distinct = True

    def get_filter_form(self):
        """
        Get FilterForm instance.
        """
        if self._filter_form is None:
            self.init_filterform()
        return self._filter_form

    def get_queryset(self):
        """
        Return queryset with filtering applied (if filter form passes
        validation).
        """
        filter_form = self.get_filter_form()
        if not filter_form is None and filter_form.is_valid():
            qs = filter_form.filter(
                super(FilterFormMixin, self).get_queryset()
            )
            if self.filter_distinct:
                qs = qs.distinct()
            return qs
        return super(FilterFormMixin, self).get_queryset()

    def get_context_data(self, **kwargs):
        """
        Add filter form to the context.
        """
        kwargs[self.context_filterform_name] = self.get_filter_form()
        return super(FilterFormMixin, self).get_context_data(**kwargs)

    def get_runtime_context(self):
        """
        Get context for filter form to allow passing runtime information,
        such as user, cookies, etc.

        Method might be overriden by implementation and context returned by
        this method will be accessible in to_lookup() method implementation
        of FilterSpec.
        """
        return {'user': self.request.user}

    def init_filterform(self):
        """
        Initiates the filter form instance and set it as a instance attribute
        to be able to cache the instance.
        """
        if not self.filter_form_cls is None:
            self._filter_form = self.filter_form_cls(
                **self.get_filter_form_kwargs(
                    data=self.request.GET,
                    runtime_context=self.get_runtime_context(),
                    use_filter_chaining=self.use_filter_chaining
                ))

    def get_filter_form_kwargs(self, **kwargs):
        """
        Provides a hook to override the initialisation kwargs of the
        filter form.
        """
        return kwargs
