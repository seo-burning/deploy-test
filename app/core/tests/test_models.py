from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='test@burningb.com', password='testpassword'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """test creating a new user with an email is successful"""
        email = 'test@burningb.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalize(self):
        """Test the email for a new user is normailized"""
        email = 'test@BURNINGB.COM'
        user = get_user_model().objects.create_user(email, 'test123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creatomg user with no email raise error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, "test123")

    def test_create_new_super_user(self):
        """test creating new super user"""
        user = get_user_model().objects.create_superuser(
            'test@burningb.com',
            'test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Girl'
        )

        self.assertEqual(str(tag), tag.name)

    def test_style_str(self):
        """test style string representation"""
        style = models.Style.objects.create(
            user=sample_user(),
            name='chic'
        )

        self.assertEqual(str(style), style.name)

    def test_influencer_str(self):
        """test the influencer string representation"""
        influencer = models.Influencer.objects.create(
            user=sample_user(),
            name='seo',
            insta_id='seonguk_seo__',
            followers=50924,
            insta_link='www.intagram.com/seonguk_seo___'
        )

        self.assertEqual(str(influencer), influencer.name)

    @patch('uuid.uuid4')
    def test_influencer_file_name_uuid(self, mock_uuid):
        """test that image is saved in the correct location"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.influencer_image_file_path(None, 'myimage.jpg')

        expected_path = f'uploads/influencer/{uuid}.jpg'
        self.assertEqual(file_path, expected_path)
