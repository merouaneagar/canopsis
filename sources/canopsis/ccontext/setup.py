from setuptools import setup, find_packages
import os

install_requires = [
    'cstorage'
]

with open(os.path.join(os.path.dirname(__file__), 'README')) as f:
    desc = f.read()

setup(
    name="ccontext",
    version="0.1",
    author="Capensis",
    author_email="canopsis@capensis.fr",
    description=("Store ccontext"),
    license="AGPL v3",
    zip_safe=False,
    keywords="ccontext storage store canopsis ccontext",
    install_requires=install_requires,
    url="http://www.canopsis.org",
    packages=find_packages(exclude="test"),
    long_description=desc,
    test_suite="test"
)
