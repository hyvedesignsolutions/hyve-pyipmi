import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()
with open('requirements.txt', 'r') as fh:
    requirements = [line.strip() for line in fh]

setuptools.setup(
    name='hyve-pyipmi',
    version='1.0.0',
    keywords=['ipmi', 'rmcp', 'rmcpp'],
    author='Janny Au',
    author_email='jannya@hyvedesignsolutions.com',
    description='Pure Python-based IPMI client developed by Hyve Design Solutions.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/hyvedesignsolutions/hyve-pyipmi',
    license='BSD 3-Clause License',
    platforms=['linux', 'windows'],
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=requirements,
)

