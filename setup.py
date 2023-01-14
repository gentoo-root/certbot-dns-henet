from setuptools import setup
from setuptools import find_packages


setup(
    name='certbot-dns-henet',
    version='0.0.0',
    description="he.net DNS Authenticator plugin for Certbot",
    url='https://bitbucket.org/qt-max/certbot-dns-henet',
    author="Maxim Mikityanskiy",
    author_email='maxtram95@gmail.com',
    license='MIT',
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Plugins',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Security',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Networking',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires = [
        'acme>=0.21.1',
        'beautifulsoup4>=4.6.3',
        'certbot>=0.21.1',
        'requests',
        'setuptools',
    ],
    entry_points={
        'certbot.plugins': [
            'dns-henet = certbot_dns_henet.dns_henet:Authenticator',
        ],
    },
)
