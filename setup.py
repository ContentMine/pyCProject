from setuptools import setup

setup(name='pycproject',
      version='0.0.3.dev',
      description='Provides basic function to read a ContentMine CProject and CTrees into python datastructures.',
      url='http://github.com/ContentMine/pyCProject',
      author='Christopher Kittel',
      author_email='web@christopherkittel.eu',
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3 :: Only'
      ],
      license='MIT',
      packages=['pycproject'],
      install_requires=[
        'lxml',
        'beautifulsoup4'
      ],
      zip_safe=False)
