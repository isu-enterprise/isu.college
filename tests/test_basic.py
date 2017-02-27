from nose.plugins.skip import SkipTest
from nose.tools import assert_raises

#@SkipTest
class BasicTests:

    def setUp(self):
        pass

    def test_something(self):
        assert 1 + 1 == 2

    def tearDown(self):
        pass
