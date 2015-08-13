from setuptools import setup, find_packages

setup(
    name="gladminds",
    version="0.0.1",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=['setuptools', 'Django==1.6.4', 'celery==3.1.18', 'MySQL-python>=1.2.4', 'gunicorn==18.0', 'django-suit==0.2.8', 
                      'django-tastypie==0.11.0', 'requests==2.7.0', 'redis==2.9.1', 'flower==0.6.0', 'south==0.8.4', 
                      'django-celery==3.1.16','parse==1.6.4', 'django-twilio==0.5.1','django-import-export==0.2.2', 
                      'suds==0.4', 'spyne==2.10.10', 'lxml==3.3.5','django-cors-headers==0.12', 
                      'django-storages==1.1.8', 'boto==2.28.0', 'django-tastypie-swagger==0.1.2', 
                      'django-otp==0.2.7', 'django-oauth2-provider==0.2.6.1', 'newrelic==2.20.0.17', 
                      'django-debug-toolbar==1.2.1', 'django-extensions==1.2.5', 'django-composite-field',
                      'django-picklefield==0.3.1', 'django-constance', 'django-registration==1.0', 'hashedin-logan',
                      'longerusername']
)
