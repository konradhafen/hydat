from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='hydat',
      version='0.0.9',
      description='Download hydrologic data',
      long_description=readme(),
      classifiers=[
            'Development Status :: 3 - Alpha',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Natural Language :: English',
            'Topic :: Scientific/Engineering :: GIS',
      ],
      keywords='hydrology, data, download, climate',
      url='https://github.com/konradhafen/hydat',
      author='Konrad Hafen',
      author_email='khafen74@gmail.com',
      license='GPLv3',
      packages=['hydat'],
      install_requires=[
            'wget', 'gdal', 'numpy'],
      include_package_data=True,
      zip_safe=False)
