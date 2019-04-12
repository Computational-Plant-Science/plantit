from collection.models import Collection
from rest_framework import serializers


class CollectionSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = Collection
        fields = ('pk', 'storage_type','base_file_path', 'name', 'description')
