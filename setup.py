from distutils.core import setup
setup(
    name = "django-google-oauth",
    packages = ["google_oauth", ],
    version = "0.5.0",
    description = "A Django application to authenticate your application, ask for user permissions and save credentials into the database for use with google api v3.",
    author = "RochApps, LLC",
    author_email = "info@rochapps.com",
    url = "http://rochapps.com/",
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ]
)
