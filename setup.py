#!/usr/bin/env python

from distutils.core import setup

with open('README.md', 'r') as readme_file:
    readme = readme_file.read()

with open('.version', 'r') as version_file:
    version = version_file.read().strip()


setup(name='cfs-state-reporter',
      version=version,
      description=readme,
      author='CASMCMS',
      author_email='joel.landsteiner@hpe.com',
      url="https://stash.us.cray.com/projects/SCMS/repos/cfs-state-reporter/browse",
      package_dir={'': 'src'},
      packages=['cfs', 'cfs.components', 'cfs.status_reporter'],
     )
