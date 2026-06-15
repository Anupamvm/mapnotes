from rest_framework import serializers
from .models import Property, SiteEvaluation, Distance


class PropertyMiniSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            'id', 'slug', 'name', 'latitude', 'longitude',
            'priority', 'status', 'asking_price', 'area_unit',
            'total_area', 'district', 'url',
        ]

    def get_url(self, obj):
        return obj.get_absolute_url()


class SiteEvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteEvaluation
        exclude = ['id', 'property']


class DistanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Distance
        exclude = ['id', 'property']


class PropertyDetailSerializer(serializers.ModelSerializer):
    evaluation = SiteEvaluationSerializer(read_only=True)
    distances = DistanceSerializer(read_only=True)
    visit_count = serializers.IntegerField(source='visits.count', read_only=True)
    note_count = serializers.IntegerField(source='notes.count', read_only=True)
    url = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = '__all__'

    def get_url(self, obj):
        return obj.get_absolute_url()
