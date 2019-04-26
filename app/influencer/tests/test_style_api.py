from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Style, Influencer

from influencer.serializers import StyleSerializer


STYLE_URL = reverse('influencer:style-list')


class PublicStyleApiTests(TestCase):
    """Test the publicly available style API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test login is required to access the endpoint"""
        res = self.client.get(STYLE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateStyleApiTests(TestCase):
    """Test private style API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@burningb.com',
            'passtest1'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_style_list(self):
        """test retrieving list of style"""
        Style.objects.create(
            user=self.user,
            name='Chic'
        )
        Style.objects.create(
            user=self.user,
            name='Cute'
        )

        res = self.client.get(STYLE_URL)

        style = Style.objects.all().order_by('-name')
        serializer = StyleSerializer(style, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_style_limited_to_user(self):
        """test style for the authenticated user are returned"""
        user2 = get_user_model().objects.create_user(
            "test2@burningb.com",
            "asfnklw14"
        )
        Style.objects.create(user=user2, name='Sexy')
        style = Style.objects.create(user=self.user, name='Chic')

        res = self.client.get(STYLE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], style.name)

    def test_create_style_success(self):
        """test style create successful"""
        payload = {
            'name': 'chic'
        }
        self.client.post(STYLE_URL, payload)
        exists = Style.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_style_invalid(self):
        """test creating invalid style failed"""
        payload = {
            'name': ''
        }
        res = self.client.post(STYLE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_styles_assigned_to_influencers(self):
        """test filtering styles by thoose assigned to influencers"""
        style1 = Style.objects.create(
            user=self.user,
            name='Chic'
        )
        style2 = Style.objects.create(
            user=self.user,
            name='Cute'
        )
        influencer = Influencer.objects.create(
            name='Sample influencer',
            insta_id='asdasf',
            followers=1234,
            insta_link='www.instagram.com',
            user=self.user
        )
        influencer.styles.add(style1)

        res = self.client.get(STYLE_URL, {'assigned_only': 1})

        serializer1 = StyleSerializer(style1)
        serializer2 = StyleSerializer(style2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_styles_assigned_unique(self):
        """test filtering styles by assigned returns unique items"""
        style1 = Style.objects.create(
            user=self.user,
            name='Chic'
        )
        Style.objects.create(
            user=self.user,
            name='Cute'
        )
        influencer1 = Influencer.objects.create(
            name='Sample influencer',
            insta_id='asdasf',
            followers=1234,
            insta_link='www.instagram.com',
            user=self.user
        )
        influencer1.styles.add(style1)
        influencer2 = Influencer.objects.create(
            name='Sample2',
            insta_id='asdasf',
            followers=1234,
            insta_link='www.instagram.com',
            user=self.user
        )
        influencer2.styles.add(style1)

        res = self.client.get(STYLE_URL, {'assigned_only': 1})
        self.assertEqual(len(res.data), 1)
