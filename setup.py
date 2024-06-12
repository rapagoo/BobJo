from setuptools import setup, Extension

module = Extension('spam', sources=['spam.c'])

setup(
    name='spam',
    version='1.0',
    description='This is a spam package',
    ext_modules=[module]
)