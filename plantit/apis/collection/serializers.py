from django.conf import settings

from plantit.collection.models import Collection
from rest_framework import serializers
from ..mixins import PinnedSerilizerMethodMixin


class CollectionSerializer(serializers.HyperlinkedModelSerializer,  PinnedSerilizerMethodMixin):
    pinned = serializers.SerializerMethodField('pinnedByUser', source='profile_pins')

    class Meta:
        model = Collection
        fields = ('pinned', 'pk', 'storage_type','base_file_path', 'name', 'description')
        extra_kwargs = {'base_file_path': {'required': False}}

    def create(self, validated_data):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user

        validated_data['base_file_path'] = settings.IRODS_BASEPATH
        collection = Collection.objects.create(user=user, **validated_data)
        collection.save()

        return collection

    def update(self, collection, validated_data):
        super().update(collection, validated_data)
        return collection
