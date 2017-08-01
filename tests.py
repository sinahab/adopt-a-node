
import unittest

from app.tests.models import *
from app.tests.test_views import *
from app.tests.test_tasks import *
from app.tests.test_aws_node_manager import *
from app.tests.test_digital_ocean_node_manager import *

if __name__ == '__main__':
    unittest.main()
