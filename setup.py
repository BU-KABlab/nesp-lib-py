"""
Backward compatibility for setuptools.
This file will be automatically used by pip if the user runs:
pip install .
"""

import setuptools

if __name__ == "__main__":
    setuptools.setup()
