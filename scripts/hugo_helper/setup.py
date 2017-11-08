from setuptools import setup, find_packages

setup(
    name='hugo_helper',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'Click',
        'PyYAML',
        'Pillow',
        'jpegtran-cffi==0.6a1',
        'python-dateutil',
        'twitter',
    ],
    entry_points='''
        [console_scripts]
        hugo_helper=hugo_helper.hugo_helper:cli
    ''',
)

