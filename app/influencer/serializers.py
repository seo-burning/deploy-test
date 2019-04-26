from rest_framework import serializers

from core.models import Tag, Style, Influencer


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class StyleSerializer(serializers.ModelSerializer):
    """Serializer for style objects"""

    class Meta:
        model = Style
        fields = ('id', 'name')
        read_only_fields = ('id',)


class InfluencerSerializer(serializers.ModelSerializer):
    """Serializer for Influencer objects"""
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    styles = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Style.objects.all()
    )

    class Meta:
        model = Influencer
        fields = (
            'id',
            'name',
            'insta_id',
            'followers',
            'insta_link',
            'tags',
            'styles',
        )
        read_only_fields = ('id',)


class InfluencerDetailSerializer(InfluencerSerializer):
    """Serialize a influencer"""
    styles = StyleSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)


class InfluencerProfileImageSerializer(serializers.ModelSerializer):
    """serializers for uploading img for influencer"""

    class Meta:
        model = Influencer
        fields = ('id', 'profile_image')
        read_only_fields = ('id',)
