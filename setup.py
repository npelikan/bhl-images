from setuptools import setup

setup(
    name='bhl-images',
    version='',
    packages=['flickr'],
    install_requires=["setuptools", "docopt"],
    url='',
    license='MIT',
    author='nickp',
    author_email='nick.pelikan@gmail.com',
    description='',
    entry_points={
        'console_scripts': [
            'bhl-images = flickr.flickr:main'
        ]
    }
)
