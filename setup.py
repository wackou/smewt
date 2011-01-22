from setuptools import setup, find_packages
import os
import smewt # for smewt.__version__

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

datafiles_exts = [ '*.png', '*.svg', '*.tmpl', '*.css', '*.html', '*.js' ]

setup(name = 'smewt',
      version = smewt.__version__,
      description = 'Smewt - a smart media manager.',
      long_description = README + '\n\n' + NEWS,
      classifiers = [], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords = 'smewt pygoo media manager video collection',
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
