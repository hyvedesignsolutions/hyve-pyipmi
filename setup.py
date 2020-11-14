#
# Copyright (c) 2020, Hyve Design Solutions Corporation.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are 
# met:
#
# 1. Redistributions of source code must retain the above copyright 
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright 
#    notice, this list of conditions and the following disclaimer in the 
#    documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of Hyve Design Solutions Corporation nor the names 
#    of its contributors may be used to endorse or promote products 
#    derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY HYVE DESIGN SOLUTIONS CORPORATION AND 
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, 
# BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND 
# FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL 
# HYVE DESIGN SOLUTIONS CORPORATION OR CONTRIBUTORS BE LIABLE FOR ANY 
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS 
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) 
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, 
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING 
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
# POSSIBILITY OF SUCH DAMAGE.
#
import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()
with open('requirements.txt', 'r') as fh:
    requirements = [line.strip() for line in fh]

setuptools.setup(
    name='hyve-pyipmi',
    version='1.0.1',
    keywords=['ipmi', 'rmcp', 'rmcpp'],
    author='Janny Au',
    author_email='jannya@hyvedesignsolutions.com',
    description='Pure Python-based IPMI client developed by Hyve Design Solutions.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/hyvedesignsolutions/hyve-pyipmi',
    license='BSD 3-Clause License',
    platforms=['linux', 'windows'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=requirements,
    packages=[
        'pyipmi',
        'pyipmi.cmds',
        'pyipmi.intf',
        'pyipmi.mesg',
        'pyipmi.util',
    ],
    package_dir={
        'pyipmi': 'src/pyipmi',
        'pyipmi.cmds': 'src/pyipmi/cmds',
        'pyipmi.intf': 'src/pyipmi/intf',
        'pyipmi.mesg': 'src/pyipmi/mesg',
        'pyipmi.util': 'src/pyipmi/util',
    },
    scripts=[
        'pyipmi',
        'pyipmr',
        'pyping',
        'pysh',
    ],
)

