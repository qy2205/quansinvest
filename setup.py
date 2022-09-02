from setuptools import setup

setup(
    name='quansinvest',
    version='0.1',
    packages=['quansinvest', 'quansinvest.data', 'quansinvest.statistics', 'quansinvest.statistics.static',
              'quansinvest.statistics.static.indicators', 'quansinvest.statistics.forward',
              'quansinvest.statistics.forward.patterns', 'quansinvest.mktvaluation', 'quansinvest.mktvaluation.relation',
              'quansinvest.mktvaluation.relation.indicators'],
    url='',
    license='',
    author='quany',
    author_email='quanyuan821@gmail.com',
    description='Investor Toolkit'
)
