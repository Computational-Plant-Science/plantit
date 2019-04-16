from plantit.collection.models import Collection, Sample
from rest_framework import serializers

class SampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sample
        fields = ('name', 'path', 'thumbnail')


class CollectionSerializer(serializers.HyperlinkedModelSerializer):
    sample_set = SampleSerializer(many=True, required=False)

    class Meta:
        model = Collection
        fields = ('pk', 'storage_type','base_file_path', 'name', 'description', 'sample_set')

    def create(self, validated_data):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user

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
