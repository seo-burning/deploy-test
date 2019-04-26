from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Style, Influencer
from influencer import serializers


class BaseInfluencerAttrViewSet(viewsets.GenericViewSet,
                                mixins.ListModelMixin,
                                mixins.CreateModelMixin):
    """Base viewset for user owned influencer attributes"""
    """
    referred documnents
    https://www.django-rest-framework.org/api-guide/viewsets/#example_3
    https://www.django-rest-framework.org/api-guide/viewsets/#genericviewset
    https://www.django-rest-framework.org/api-guide/serializers/#modelserializer
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(influencer__isnull=False)
        return queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()

    def perform_create(self, serializer):
        """create a new object"""
        serializer.save(user=self.request.user)


class TagViewSet(BaseInfluencerAttrViewSet):
    """Manage tags in the database"""
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class StyleViewSet(BaseInfluencerAttrViewSet):
    """Manage style in the database"""
    queryset = Style.objects.all()
    serializer_class = serializers.StyleSerializer


class InfluencerViewSet(viewsets.ModelViewSet):
    """Manage influencer in the database"""
    serializer_class = serializers.InfluencerSerializer
    queryset = Influencer.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def _params_to_inst(self, qs):
        """Covert a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve the influencers for the authenticated user"""
        tags = self.request.query_params.get('tags')
        styles = self.request.query_params.get('styles')
        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_inst(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if styles:
            style_ids = self._params_to_inst(styles)
            queryset = queryset.filter(styles__id__in=style_ids)
        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.InfluencerDetailSerializer
        elif self.action == 'upload_profile_image':
            return serializers.InfluencerProfileImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """create a new influencer"""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-profile-image')
    def upload_profile_image(self, request, pk=None):
        """upload an profile image to a influencer"""
        influencer = self.get_object()
        serializer = self.get_serializer(
            influencer,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
