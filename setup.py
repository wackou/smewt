from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()

version = '0.2b1'

install_requires = [
    # List your project dependencies here.
    # For more details, see:
    # http://packages.python.org/distribute/setuptools.html#declaring-dependencies
    'pygoo',
    'pycurl',
    'cheetah',
    'lxml',
    'feedparser'
]

## media_imports = []
## for root, dirs, files in os.walk('smewt/media'):
##     media_imports += [ os.path.join(root, '*.' + ext)[6:] for ext in ('png', 'tmpl', 'css', 'html', 'js') ]

## icons_imports = [ 'icons/*.' + ext for ext in ('png', 'svg') ]

datafiles_exts = [ '*.png', '*.svg', '*.tmpl', '*.css', '*.html', '*.js' ]

setup(name = 'smewt',
      version = version,
      description = 'Smewt - a smart media manager.',
      long_description = README + '\n\n' + NEWS,
      classifiers = [], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords = 'pygoo object graph mapper',
      author = 'Nicolas Wack',
      author_email = 'wackou@gmail.com',
      url = 'http://www.smewt.com/',
      license = 'GPLv3',
      packages = find_packages(exclude = [ 'ez_setup', 'examples', 'tests' ]),
      #package_data = dict((package, datafiles_exts) for package in find_packages()),
      include_package_data = True,
      scripts = [ 'bin/smewg' ],
      install_requires = install_requires
      )
