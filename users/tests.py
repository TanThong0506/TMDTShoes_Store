from django.test import TestCase

from django.contrib.auth.models import User
from .models import ChatMessage


class ChatMessageTests(TestCase):
	def test_chatmessage_str_and_ordering(self):
		u = User.objects.create_user(username='u1')
		m1 = ChatMessage.objects.create(user=u, message='Hello', is_bot=False)
		m2 = ChatMessage.objects.create(user=None, message='Bot reply', is_bot=True)
		# ordering by created_at defined in Meta
		qs = list(ChatMessage.objects.all())
		self.assertEqual(qs[0].message, 'Hello')
		self.assertIn('Hello', str(m1))
