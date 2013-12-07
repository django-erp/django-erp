#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This file is part of the django ERP project.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

__author__ = 'Emanuele Bertoldi <emanuele.bertoldi@gmail.com>'
__copyright__ = 'Copyright (c) 2013 Emanuele Bertoldi'
__version__ = '0.0.2'

from django.test import TestCase
from django.contrib.auth import get_user_model

from . import *
from ..models import *
from ..backends import *

class ObjectPermissionBackendTestCase(TestCase):
    def test_always_fail_authentication(self):
        """Tests the (unsupported) user authentication must always fail.
        """
        u, n = get_user_model().objects.get_or_create(username="u", password="password")
        
        self.assertEqual(ob.authenticate("u1", "password"), None)
        
    def test_has_perm(self):
        """Tests simple object permissions between three different instances.
        """
        u, n = get_user_model().objects.get_or_create(username="u")
        u1, n = get_user_model().objects.get_or_create(username="u1")
        u2, n = get_user_model().objects.get_or_create(username="u2")
        p = Permission.objects.get_by_natural_key("delete_user", auth_app, "user")
        
        self.assertFalse(ob.has_perm(u, p, u1))
        self.assertFalse(ob.has_perm(u, p, u2))
        
        u1.user_permissions.add(p)
        
        # Please keep in mind that ObjectPermissionBackend only takek in account
        # row/object-level permissions over a certain model instance, without
        # knowing anything about model-level permissions over its model class.
        self.assertFalse(ob.has_perm(u1, p, u))
        self.assertFalse(ob.has_perm(u1, p, u2))
        
        op, n = ObjectPermission.objects.get_or_create(object_id=u.pk, perm=p)
        op.users.add(u2)
        
        self.assertTrue(ob.has_perm(u2, p, u))
        self.assertFalse(ob.has_perm(u2, p, u1))
        
    def test_superuser_has_always_perm(self):
        """Tests that a superuser must have global perms on everything.
        """
        class TestObject(object):
            pk = 2894328923984238943298
            
        obj = TestObject()
        su, n = get_user_model().objects.get_or_create(username="superuser", is_superuser=True)
        
        p = Permission.objects.get_by_natural_key("delete_user", auth_app, "user")
        
        self.assertTrue(ob.has_perm(su, p, obj))
        
    def test_anonymous_has_never_perm(self):
        """Tests that an anonymous user doesn't have any perms on anything.
        """
        class TestObject(object):
            pk = 5894325454554428943296
            
        def fake_is_anonymous():
            return True
            
        obj = TestObject()
        au, n = get_user_model().objects.get_or_create(username="anonymous")
        au.is_anonymous = fake_is_anonymous
        
        p = Permission.objects.get_by_natural_key("delete_user", auth_app, "user")
        
        self.assertFalse(ob.has_perm(au, p, obj))
        
    def test_has_perm_by_name(self):
        """Tests retrieving object permissions by names.
        """
        p_name = "%s.delete_user" % auth_app
        
        u, n = get_user_model().objects.get_or_create(username="u")
        u1, n = get_user_model().objects.get_or_create(username="u1")
        u2, n = get_user_model().objects.get_or_create(username="u2")
        
        p = Permission.objects.get_by_natural_key("delete_user", auth_app, "user")
        op, n = ObjectPermission.objects.get_or_create(object_id=u.pk, perm=p)
        op.users.add(u2)
        
        self.assertTrue(ob.has_perm(u2, p_name, u))
        self.assertFalse(ob.has_perm(u2, p_name, u1))
