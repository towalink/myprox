import os
import setuptools


with open('README.md', 'r') as f:
    long_description = f.read()

setup_kwargs = {
    'name': 'MyProx',
    'version': '0.5.0',
    'author': 'Dirk Henrici',
    'author_email': 'pypi.myprox@henrici.name',
    'description': 'simple web frontend for Proxmox VE users',
    'long_description': long_description,
    'long_description_content_type': 'text/markdown',
    'url': 'https://www.github.com/towalink/myprox',
    'packages': setuptools.find_packages('src'),
    'package_dir': {'': 'src'},
    'include_package_data': True,
    'install_requires': ['cherrypy',
                         'requests',
                         'jinja2',
                         'proxmoxer',
                        ],
    'entry_points': '''
        [console_scripts]
        myprox=myprox:main
    ''',
    'classifiers': [
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Operating System :: POSIX :: Linux',
        'Development Status :: 4 - Beta',
        #'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Information Technology',
        'Topic :: System :: Systems Administration',
        'Framework :: CherryPy',
    ],
    'python_requires': '>=3.6',
    'keywords': 'Proxmox frontend gui',
    'project_urls': {
        'Project homepage': 'https://www.henrici.name/projects/myprox',
        'Repository': 'https://www.github.com/towalink/myprox',
        'Documentation': 'https://www.github.com/towalink/myprox',
    },
}


if __name__ == '__main__':
    setuptools.setup(**setup_kwargs)
