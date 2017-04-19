# coding=utf-8
import unittest
from app.models import User, Role, AnonymousUser, Permissions


class UserModelTestCase(unittest.TestCase):

    def test_password_setter(self):
        u = User(password='dog')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='dog')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='dog')
        self.assertTrue(u.verify_password('dog'))
        self.assertFalse(u.verify_password('cat'))

    def test_password_salts_are_random(self):
        u = User(password='dog')
        u2 = User(password='dog')
        self.assertFalse(u.password_hash == u2.password_hash)

    def test_roles_and_permissions(self):
        Role.insert_roles()
        u = User(email='test@test.com', password='test')
        self.assertTrue(u.can(Permissions.WRITE_ARTICLES))
        self.assertFalse(u.can(Permissions.MODERATE_COMMENTS))

    def test_anonymouse_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permissions.FOLLOW))
