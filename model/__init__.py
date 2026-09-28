"""
LPARA Machine Learning Model Suite
Laptop Price Adaptive Regression Algorithm
"""

import os
import sys

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(PACKAGE_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

__version__ = "1.0.0"
