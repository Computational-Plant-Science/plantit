from django.conf import settings

from plantit.datasets.models import Dataset
from rest_framework import serializers


class CollectionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Dataset
        fields = ('pk', 'storage_type','base_file_path', 'name', 'description')
        extra_kwargs = {'base_file_path': {'required': False}}

    def create(self, validated_data):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user

        validated_data['base_file_path'] = settings.IRODS_BASEPATH
        collection = Dataset.objects.create(user=user, **validated_data)
        collection.save()

        return collection

    def update(self, collection, validated_data):
        super().update(collection, validated_data)
        return collection
