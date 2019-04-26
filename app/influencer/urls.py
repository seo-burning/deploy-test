from django.urls import path, include
from rest_framework.routers import DefaultRouter

from influencer import views


router = DefaultRouter()
router.register('tags', views.TagViewSet)
router.register('style', views.StyleViewSet)
router.register('influencer', views.InfluencerViewSet)


app_name = 'influencer'

urlpatterns = [
    path('', include(router.urls))
]
