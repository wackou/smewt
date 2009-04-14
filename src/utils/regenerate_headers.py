#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008 Nicolas Wack <wackou@gmail.com>
#
# Smewt is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Smewt is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


from smewt.utils import GlobDirectoryWalker
from subprocess import Popen,  PIPE
import os

header = '''#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
'''

license = '''#
# Smewt is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Smewt is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
'''


def getLicenseHeader(filename):
    '''Returns the license header for a file, with copyright info and GPL license.
    Authors are fetched from the git log.'''
    cmd = 'git log --reverse --pretty=format:"%an <%ae> - %aD" ' + filename
    result = Popen(cmd,  shell=True, stdout=PIPE).stdout.read()

    if not result:
        raise EnvironmentError('file is not under version control')

    authors = {}
    for line in result.strip().split('\n'):
        (author, date) = line.split(' - ')
        year = date.split(' ')[3]
        try:
            authors[author].add(year)
        except:
            authors[author] = set()
            authors[author].add(year)

    lh = header
    for author in authors:
        years = sorted(authors[author])
        authline = '# Copyright (c) ' + years[0]
        for year in years[1:]:
            authline += ',' + year
        authline += ' ' + author + '\n'
        lh += authline

    lh += license

    return lh

if __name__ == '__main__':
    for filename in GlobDirectoryWalker(os.getcwd(), ['*.py']):
        try:
            licenseHeader = getLicenseHeader(filename)

            source = open(filename).read()
            sourceParts = source.split(license)

            if len(sourceParts) == 1:
                # there was no header information present
                newSource = licenseHeader + sourceParts[0]
                print 'adding header for:',  filename
                open(filename,  'w').write(newSource)
            else:
                # there was a header already present, update it if different
                newSource = licenseHeader + license.join(sourceParts[1:])
                if source != newSource:
                    print 'updating header for:',  filename
                    open(filename,  'w').write(newSource)

        except: pass
