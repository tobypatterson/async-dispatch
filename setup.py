from setuptools import setup

setup(name='async-dispatch',
      version='0.1',
      description='Dispatches events from a publisher to any number of subscribers.',
      url='https://github.com/tobypatterson/async-dispatch/',
      author='Toby Patterson',
      author_email='me@tobys.email',
      license='MIT',
      py_modules=['async_dispatch'],
      tests_require=[
          'pytest',
      ],
      classifiers=[
         'Intended Audience :: Developers',
         'Programming Language :: Python :: 3.5',
	 'Topic :: Communications'
      ],
      extras_require={
          ':python_version == "3.5"': ['asyncio']
      },
)
