from setuptools import setup

setup(name='async-dispatch',
      version='0.1',
      description='Dispatches events from a publisher to any number of subscribers.',
      py_modules=['async_dispatch'],
      setup_requires=[
          'pytest-runner',
      ],
      tests_require=[
          'pytest',
      ],
)