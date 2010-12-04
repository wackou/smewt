from distutils.core import setup
from setuptools import find_packages
import os

media_imports = []
for root, dirs, files in os.walk('smewt/media'):
    media_imports += [ os.path.join(root, '*.' + ext)[6:] for ext in ('png', 'tmpl', 'css', 'html', 'js') ]

icons_imports = [ 'icons/*.' + ext for ext in ('png', 'svg') ]

print '*'*100
print find_packages()

setup(
    name = 'Smewt',
    version = '0.2',
    author = 'Nicolas Wack',
    author_email = 'wackou@gmail.com',
    packages = find_packages(),
    #package_data = { 'smewt': media_imports + icons_imports },
    package_data = dict((package, [ '*.png', '*.svg', '*.tmpl', '*.css', '*.html', '*.js' ]) for package in find_packages()),
    scripts = [ 'bin/smewg' ],
    url = 'http://www.smewt.com/',
    license = 'LICENSE.txt',
    description = 'Smewt - a smart media manager.',
    long_description = open('README.txt').read(),

    install_requires = [ 'pygoo', 'pycurl', 'cheetah', 'lxml', 'feedparser' ]
)
