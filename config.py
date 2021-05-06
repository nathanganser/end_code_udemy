import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://xzruhowkodfply:c35a47e137e1ace774581beaee816314e152f72123e5c1cbe451694b931cb832@ec2-54-155-87-214.eu-west-1.compute.amazonaws.com:5432/dcj9v5e9cm8j0u'
