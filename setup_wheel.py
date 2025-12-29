
from setuptools import setup, find_packages
setup(
    name='sqlcipher3-binary',
    version='4.12.0',
    packages=['sqlcipher3'],
    package_data={'sqlcipher3': ['*.pyd']},
    include_package_data=True,
    zip_safe=False,
)
