from setuptools import setup, find_packages


def readme():
    # for long description
    with open('README.md') as f:
        return f.read()


module_name = 'pycausal'

setup(name=module_name,
      version='0.0',
      description='A Python module for causal reasoning',
      long_description=readme(),
      url='https://github.com/andrew31416/py-causal',
      license='MIT',
      install_requires=['networkx',
                        'numpy',
                        'typing'
                        ],
      packages=find_packages(),
      classifiers=['Development Status :: 1 - Planning']
      )