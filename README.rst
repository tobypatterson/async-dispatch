Async Dispatch
=============

Python Asyncio-enabled Event Dispatcher Based on Publishers and Subscribers

Build Status
------------

.. image:: https://travis-ci.org/tobypatterson/async-dispatch.svg?branch=master

Requirements
------------

Async Dispatch uses the keywords async and await, and thus requires Python 3.5 or greater. This version of Python is distributed in the most recent release of Ubuntu 16.04, and can be easily installed on Mac OS X using brew .

Installation
------------

The prefered way to install Async Dispatch for Python 3.5 is using pip:. 

.. code:: bash

   pip install async-dispatch

Basic Usage
-----------

Documentation will soon be available on readthedocs.  Here is a brief summary.

.. code:: python

   publisher = BasicPublisher()
   subscriber = BasicSubscriber()

   loop = asyncio.get_event_loop()

   server = Dispatcher(publisher, subscriber, loop=loop)
   loop.run_until_complete(server.start(max_events=5))
