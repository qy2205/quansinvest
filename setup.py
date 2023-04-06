from setuptools import setup

setup(
    name='quansinvest',
    version='0.1',
    package_data={'quansinvest': ['resources/*.csv']},
    packages=[
        'quansinvest',
        'quansinvest.data',
        'quansinvest.evaluation', 'quansinvest.evaluation.metrics',
        'quansinvest.leaderboard',
        'quansinvest.mktvaluation', 'quansinvest.mktvaluation.relation', 'quansinvest.mktvaluation.indicators',
        'quansinvest.statistics', 'quansinvest.statistics.static', 'quansinvest.statistics.static.indicators',
        'quansinvest.statistics.forward', 'quansinvest.statistics.forward.patterns',
        'quansinvest.stockvaluation',
        'quansinvest.utils',
        'quansinvest.resources'
    ],
    url='',
    license='',
    author='quany',
    author_email='quanyuan821@gmail.com',
    description='Investor Toolkit'
)

