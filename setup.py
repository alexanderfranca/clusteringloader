from setuptools import setup
from setuptools.command.install import install
from os.path import expanduser
from shutil import copyfile

setup(
    name='ClusteringLoader',
    version='0.1',
    author='Franca AF (Alexander da Franca Fernandes)',
    author_email='alexander@francafernandes.com.br',
    license='BSD',
    description='Tool to import clustering results to AnEnDB relational database.',
    long_description='Tool to import clustering results to AnEnDB relational database.',
    packages=[ 'clusteringloader' ],
    scripts=['bin/clusteringloader'],
    platforms='Linux',
    url='http://bioinfoteam.fiocruz.br/clusteringloader',
    install_requires=[
            'datetime ',
            ],
)


