from setuptools import setup, find_namespace_packages

setup(
    name='webpushcrawler',
    description='Automatically open and handle WebPush notifications.',
    version='0.0.1',
    author='Alexander Becker',
    license='GNU AGPLv3',
    platforms='Linux',
    packages=find_namespace_packages(include=['webpushcrawler.*'])
)
