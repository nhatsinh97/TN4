import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import Config

def test_debug_flag():
    assert isinstance(Config.DEBUG, bool)
    assert Config.DEBUG is (Config.ENV == 'development')
