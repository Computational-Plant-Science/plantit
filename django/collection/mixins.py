class CastableModelMixin:
    """
    Add support to cast an object to its final class

    Borrowed from https://sophilabs.co/blog/castable-model-mixin
    """

    def cast(self):
        cls = self.__class__
        subclasses = cls.all_subclasses()

        if len(subclasses) == 0:
            return self

        for subclass in subclasses:
            try:
                obj = getattr(self, subclass._meta.model_name, None)
                if obj is not None:
                    # select_related doesn't fill child with parent relateds
                    descriptors = [getattr(cls, field.name)
                                   for field in cls._meta.get_fields()
                                   if field.is_relation and field.many_to_one]
                    for descriptor in descriptors:
                        if descriptor.is_cached(self):
                            setattr(obj,
                                    descriptor.cache_name,
                                    getattr(self, descriptor.cache_name))
                    if hasattr(self, '_prefetched_objects_cache'):
                        obj._prefetched_objects_cache = \
                            self._prefetched_objects_cache
                    return obj
            except ObjectDoesNotExist:
                pass

        return self

    @classmethod
    def all_subclasses_model_names(cls):
        model_names = []
        for subclass in cls.all_subclasses():
            if not (subclass._meta.proxy or subclass._meta.abstract):
                model_names.append(subclass._meta.model_name)
        return model_names

    @classmethod
    def all_subclasses(cls):
        return [g for s in cls.__subclasses__() for g in s.all_subclasses()] + cls.__subclasses__()

    @property
    def model(self):
        return self.cast()._meta.model_name

    @property
    def verbose_name(self):
        return self.cast()._meta.verbose_name.capitalize()

class CastableQuerySetMixin:
    def select_related_subclasses(self):
        return self.select_related(*[subclass._meta.model_name for subclass in self.model.all_subclasses()
                                     if not subclass._meta.proxy])
