from django.test import TestCase
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from users.models import User


@pytest.mark.django_db
def test_user_creation():
    user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass")
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.check_password("testpass")

@pytest.mark.django_db
def test_user_list_api():
    client = APIClient()
    url = reverse("api:users-list")
    response = client.get(url)
    assert response.status_code == 200
    assert "results" in response.data
