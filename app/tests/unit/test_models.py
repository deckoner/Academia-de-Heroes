import pytest
from django.test import TestCase


@pytest.mark.unit
class TestPersonajeModel(TestCase):
    
    def test_dummy_paso(self):
        self.assertEqual(1 + 1, 2)