import tempfile
import os
from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Influencer, Tag, Style

from influencer.serializers import InfluencerSerializer, \
                                   InfluencerDetailSerializer


INFLUENCERS_URL = reverse('influencer:influencer-list')


def profile_image_upload_url(influencer_id):
    """return URL for influencer image upload"""
    return reverse('influencer:influencer-upload-profile-image',
                   args=[influencer_id])


def detail_url(influencer_id):
    """return influencer detail url"""
    return reverse('influencer:influencer-detail', args=[influencer_id])


def sample_tag(user, name='main'):
    """create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_style(user, name='chic'):
    """create and return a sample style"""
    return Style.objects.create(user=user, name=name)


def sample_influencer(user, **params):
    """Create and return a sample influencer"""
    defaults = {
        'name': 'Sample influencer',
        'insta_id': 'asdasf',
        'followers': 1234,
        'insta_link': 'www.instagram.com'
    }
    defaults.update(params)

    return Influencer.objects.create(user=user, **defaults)


class PublicInfluencerApiTests(TestCase):
    """Test unauthenticated influencer API access"""

    def setUp(self):
        self.client = APIClient()

    def test_required_auth(self):
        """Test the authenticaiton is required"""
        res = self.client.get(INFLUENCERS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateInfluencerApiTests(TestCase):
    """Test authenticated influencer API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@burningb.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_influencers(self):
        """Test retrieving list of influencers"""
        sample_influencer(user=self.user)
        sample_influencer(user=self.user)

        res = self.client.get(INFLUENCERS_URL)

        influencers = Influencer.objects.all().order_by('-id')
        serializer = InfluencerSerializer(influencers, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_influencers_limited_to_user(self):
        """Test retrieving influencers for user"""
        user2 = get_user_model().objects.create_user(
            'other@burningb.com',
            'pass'
        )
        sample_influencer(user=user2)
        sample_influencer(user=self.user)

        res = self.client.get(INFLUENCERS_URL)

        influencers = Influencer.objects.filter(user=self.user)
        serializer = InfluencerSerializer(influencers, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_influencer_detail(self):
        """test viewing influencer detail page"""
        influencer = sample_influencer(user=self.user)
        influencer.tags.add(sample_tag(user=self.user))
        influencer.styles.add(sample_style(user=self.user))

        url = detail_url(influencer.id)
        res = self.client.get(url)

        serializer = InfluencerDetailSerializer(influencer)

        self.assertEqual(res.data, serializer.data)

    def test_create_basic_influencer(self):
        """test creating influencer"""
        payload = {
            'name': 'Sample influencer',
            'insta_id': 'asdasf',
            'followers': 1234,
            'insta_link': 'www.instagram.com',
        }
        res = self.client.post(INFLUENCERS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        influencer = Influencer.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(influencer, key))

    def test_create_influencer_with_tags(self):
        """test creating influencer with tags"""
        tag1 = sample_tag(user=self.user, name='GOOD')
        tag2 = sample_tag(user=self.user, name='FINE')
        payload = {
            'name': 'Sample influencer',
            'insta_id': 'asdasf',
            'followers': 1234,
            'insta_link': 'www.instagram.com',
            'tags': [tag1.id, tag2.id],
        }
        res = self.client.post(INFLUENCERS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        influencer = Influencer.objects.get(id=res.data['id'])
        tags = influencer.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_influencer_with_styles(self):
        """test creating influencer with styles"""
        style1 = sample_style(user=self.user, name='CHIC')
        style2 = sample_style(user=self.user, name='CUTE')
        payload = {
            'name': 'Sample influencer',
            'insta_id': 'asdasf',
            'followers': 1234,
            'insta_link': 'www.instagram.com',
            'styles': [style1.id, style2.id],
        }
        res = self.client.post(INFLUENCERS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        influencer = Influencer.objects.get(id=res.data['id'])
        styles = influencer.styles.all()
        self.assertEqual(styles.count(), 2)
        self.assertIn(style1, styles)
        self.assertIn(style2, styles)

    def test_partical_update_influencer(self):
        """test partical update a influencer with patch"""
        influencer = sample_influencer(user=self.user)
        influencer.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='Cry')

        payload = {
            'name': 'Great Park',
            'tags': [new_tag.id]
        }
        url = detail_url(influencer.id)
        self.client.patch(url, payload)

        influencer.refresh_from_db()
        self.assertEqual(influencer.name, payload['name'])
        tags = influencer.tags.all()
        self.assertEqual(tags.count(), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_influencer(self):
        """test update influencer with put"""
        influencer = sample_influencer(user=self.user)
        influencer.tags.add(sample_tag(user=self.user))

        payload = {
            'name': 'Great Seo',
            'insta_id': 'aasdsasdasf',
            'followers': 12324,
            'insta_link': 'www.instagram.com/serongnks',
        }
        url = detail_url(influencer.id)
        self.client.put(url, payload)

        influencer.refresh_from_db()
        self.assertEqual(influencer.name, payload['name'])
        self.assertEqual(influencer.insta_id, payload['insta_id'])
        self.assertEqual(influencer.followers, payload['followers'])
        self.assertEqual(influencer.insta_link, payload['insta_link'])
        tags = influencer.tags.all()
        self.assertEqual(tags.count(), 0)


class InfluencerProfileImageUploadTests(TestCase):
    """profile_image upload test"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@burningb.com',
            'anlsgkmsakl213'
        )
        self.client.force_authenticate(self.user)
        self.influencer = sample_influencer(user=self.user)

    def tearDown(self):
        self.influencer.profile_image.delete()

    def test_upload_profile_image(self):
        """test upload profile_image"""
        url = profile_image_upload_url(self.influencer.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'profile_image': ntf},
                                   format='multipart')

        self.influencer.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('profile_image', res.data)
        self.assertTrue(os.path.exists(self.influencer.profile_image.path))

    def test_upload_invalid_profile_image_to_influencer(self):
        """test uploading invalit image"""
        url = profile_image_upload_url(self.influencer.id)
        res = self.client.post(url, {'profile_image': 'notimage'},
                               format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_influencers_by_tags(self):
        """test returning influencers with specific tags"""
        influencer1 = sample_influencer(user=self.user, name='Park')
        influencer2 = sample_influencer(user=self.user, name='Seo')
        influencer3 = sample_influencer(user=self.user, name='Hong')
        tag1 = sample_tag(user=self.user, name='Solo')
        tag2 = sample_tag(user=self.user, name='Couple')
        influencer1.tags.add(tag1)
        influencer2.tags.add(tag2)

        res = self.client.get(
            INFLUENCERS_URL,
            {'tags': f'{tag1.id}, {tag2.id}'}
        )

        serializer1 = InfluencerSerializer(influencer1)
        serializer2 = InfluencerSerializer(influencer2)
        serializer3 = InfluencerSerializer(influencer3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_influencer_by_style(self):
        """test returning influencers with specific styles"""
        influencer1 = sample_influencer(user=self.user, name='Park')
        influencer2 = sample_influencer(user=self.user, name='Seo')
        influencer3 = sample_influencer(user=self.user, name='Hong')
        style1 = sample_style(user=self.user, name='Chic')
        style2 = sample_style(user=self.user, name='Lovely')
        influencer1.styles.add(style1)
        influencer2.styles.add(style2)

        res = self.client.get(
            INFLUENCERS_URL,
            {'styles': f'{style1.id}, {style2.id}'}
        )

        serializer1 = InfluencerSerializer(influencer1)
        serializer2 = InfluencerSerializer(influencer2)
        serializer3 = InfluencerSerializer(influencer3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)
