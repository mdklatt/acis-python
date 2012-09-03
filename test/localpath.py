""" Add local directory root to the path.

"""
import os
import sys

root = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), root))

