from distutils.core import setup
from setuptools import find_packages
import os

media_imports = []
for root, dirs, files in os.walk('smewt/media'):
    media_imports += [ os.path.join(root, '*.' + ext)[6:] for ext in ('png', 'tmpl', 'css', 'html', 'js') ]

icons_imports = [ 'icons/*.' + ext for ext in ('png', 'svg') ]


setup(
    name = 'Smewt',
    version = '0.2',
    author = 'Nicolas Wack',
    author_email = 'wackou@gmail.com',
    packages = find_packages(),
    package_data = { 'smewt': media_imports + icons_imports },
    scripts = [ 'bin/smewg.py' ],
    url = 'http://www.smewt.com/',
    license = 'LICENSE.txt',
    description = 'Smewt - a smart media manager.',
    long_description = open('README.txt').read(),

    install_requires = [ 'pycurl', 'cheetah', 'lxml', 'imdbpy', 'feedparser' ]
)
