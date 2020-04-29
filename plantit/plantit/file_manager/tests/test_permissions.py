import tempfile

from django.test import TestCase
from plantit.job_manager.test.test_models import create_user

from ..permissions import *
from ..filesystems import registrar
from ..filesystems.local import Local

# Create your tests here.
#class TestPermissions(TestCase):
#    @classmethod
#    def setUpTestData(cls):
#        cls.storage = 'local'
#
#    def check_always_denied_local(self,user):
#        """
#            Directories that should always be denied access
#        """
#        self.assertFalse(Permissions.allowed(user,self.storage,"./files/tmp/"))
#        self.assertFalse(Permissions.allowed(user,self.storage,"./files/tmpgTrmo"))
#        self.assertFalse(Permissions.allowed(user,self.storage,"files/tmp/"))
#        self.assertFalse(Permissions.allowed(user,self.storage,"files/tmp"))
#        self.assertFalse(Permissions.allowed(user,self.storage,"./files/"))
#        self.assertFalse(Permissions.allowed(user,self.storage,"./files"))
#        self.assertFalse(Permissions.allowed(user,self.storage,"files/"))
#        self.assertFalse(Permissions.allowed(user,self.storage,"files"))
#        self.assertFalse(Permissions.allowed(user,self.storage,"./"))
#        self.assertFalse(Permissions.allowed(user,self.storage,""))
#        self.assertFalse(Permissions.allowed(user,self.storage,"/"))
#
#    def test_valid_access(self):
#        with tempfile.TemporaryDirectory(dir="./files/tmp/") as dir:
#            user = create_user()
#            denied_user = create_user()
#
#            Permissions.allow(user,self.storage, dir)
#
#            self.assertTrue(Permissions.allowed(user,self.storage,dir))
#            self.assertTrue(Permissions.allowed(user,self.storage,dir + "/test/"))
#            self.assertFalse(Permissions.allowed(denied_user,self.storage,dir))
#            self.assertFalse(Permissions.allowed(denied_user,self.storage,dir + "/test/"))
#
#            #Check variations
#            self.check_always_denied_local(user)
#            registrar.register(Local(name="Hacker"))
#            self.assertFalse(Permissions.allowed(user,"Hacker",dir),
#                "Access to other storage systems should be denied.")
#
#    def test_revoked_access(self):
#        with tempfile.TemporaryDirectory(dir="./files/tmp/") as dir:
#            user = create_user()
#
#            Permissions.allow(user,self.storage,dir)
#            Permissions.allow(user,self.storage,dir + "/test/")
#
#            Permissions.revoke(user,self.storage,dir)
#            self.assertFalse(Permissions.allowed(user,self.storage,dir + "/test/"))
#            self.assertFalse(Permissions.allowed(user,self.storage,dir))
#
#            #Check variations
#            self.check_always_denied_local(user)
#
#    def test_parent_folder_access(self):
#        with tempfile.TemporaryDirectory(dir="./files/tmp/") as dir:
#            user = create_user()
#
#            Permissions.allow(user,self.storage,dir)
#
#            self.assertFalse(Permissions.allowed(user,self.storage,dir + "/../"),
#                "Access to parent folder via ../ should be denined")
