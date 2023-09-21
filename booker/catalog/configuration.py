"""

"""
import os
# if container mode is set to true,
# environment variables are used to configure mysql database with .env file
# if set to false, database paremeters are defined in settings.py
container_mode = True

environment = os.environ.get('ENV', 'dev')

if environment == 'prd':
    storage_directory = '/volumes/homes/web_library'
else:
    storage_directory = '/volumes/homes/Alex/ebook/test'