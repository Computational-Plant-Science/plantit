from plantit.collection.models import Collection, Sample
from plantit.stores import registrar
from rest_framework import serializers
from ..mixins import PinnedSerilizerMethodMixin

class SampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sample
        fields = ('pk','name', 'path', 'thumbnail_supported', 'thumbnail', 'metadata')
        extra_kwargs = {
            'thumbnail': {
                'read_only': True,
            },
        }

class CollectionSerializer(serializers.HyperlinkedModelSerializer,  PinnedSerilizerMethodMixin):
    sample_set = SampleSerializer(many=True, required=False)

    pinned = serializers.SerializerMethodField('pinnedByUser', source='profile_pins')

    class Meta:
        model = Collection
        fields = ('pinned', 'pk', 'storage_type','base_file_path', 'name', 'description', 'sample_set', 'metadata')
        extra_kwargs = {'base_file_path': {'required': False}}

    def create(self, validated_data):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user

        validated_data['base_file_path'] = registrar.default_path(validated_data['storage_type'], user)
        collection = Collection(**validated_data,user=user)
        collection.save()

        return collection

    def update(self, collection, validated_data):
        print("Request to update collection with: %s"%(validated_data))

        sample_data = validated_data.pop('sample_set',None)
        if(sample_data):
            for sample in sample_data:
                collection.add_sample(**sample)

        super().update(collection, validated_data)

        return collection
