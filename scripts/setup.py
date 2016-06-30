from setuptools import setup

setup(
    name='hugo_helper',
    version='0.1',
    py_modules=['hugo_helper'],
    install_requires=[
        'Click',
        'PyYAML',
        'Pillow',
    ],
    entry_points='''
        [console_scripts]
        hugo_helper=hugo_helper:cli
    ''',
)
