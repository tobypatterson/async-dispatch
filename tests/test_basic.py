import pytest

import asyncio
import time

import sys
from os.path import dirname, abspath

parent_path = dirname(dirname(abspath(__file__)))
sys.path.append(parent_path)

from async_dispatch import Dispatcher, SubscriberInterface, PublisherInterface, Event


class BasicSubscriber(SubscriberInterface):

    listen_to_events = ['test']

    def __init__(self):

        self.total = 0

    async def consume(self, event):

        event_name, timestamp, payload = event

        self.total += int(payload)

    def get_total(self):

        return self.total


class BasicSubscriber2(BasicSubscriber):

    listen_to_events = {
        'test': 'update'
    }

    async def update(self, event):

        await self.consume(event)


class BasicPublisher(PublisherInterface):

    count = 0
    async def produce(self):

        cls = self.__class__
        v = cls.count
        cls.count += 1

        return Event('test', time.time(), v)


class BadPublisher(PublisherInterface):

    async def produce(self):

        return "not an event"


def test_basic_dispatch():

    publisher = BasicPublisher()
    subscriber = BasicSubscriber()

    loop = asyncio.get_event_loop()

    server = Dispatcher(publisher, subscriber, loop=loop)
    loop.run_until_complete(server.start(max_events=5))


def test_custom_handler():

    publisher = BasicPublisher()
    subscriber = BasicSubscriber2()

    loop = asyncio.get_event_loop()

    server = Dispatcher(publisher, [subscriber], loop=loop)
    loop.run_until_complete(server.start(max_events=5))


def test_wrong_max_events():

    loop = asyncio.get_event_loop()
    server = Dispatcher(loop=loop)

    with pytest.raises(ValueError):
        loop.run_until_complete(server.start(max_events=-1))

    with pytest.raises(ValueError):
        loop.run_until_complete(server.start(max_events="1"))


def test_bad_event():

    publisher = BadPublisher()
    subscriber = BasicSubscriber2()

    loop = asyncio.get_event_loop()

    with pytest.raises(TypeError):

        server = Dispatcher(publisher, subscriber, loop=loop)
        loop.run_until_complete(server.start(max_events=1))


def test_not_implemented():

    publisher = PublisherInterface()
    subscriber = SubscriberInterface()

    loop = asyncio.get_event_loop()

    with pytest.raises(NotImplementedError):

        server = Dispatcher(publisher, subscriber, loop=loop)
        loop.run_until_complete(server.start(max_events=1))


def test_wrong_publisher_type():

    publisher = object()
    subscriber = BasicSubscriber()

    loop = asyncio.get_event_loop()

    with pytest.raises(TypeError):
        server = Dispatcher(publisher, subscriber, loop=loop)

    # A publisher without the publish method
    publisher = BasicPublisher()
    publisher.produce = None

    with pytest.raises(TypeError):
        server = Dispatcher(publisher, subscriber, loop=loop)

def test_wrong_subscriber_type():

    server = Dispatcher()

    with pytest.raises(TypeError):
        server.add_subscriber(object())

def test_add_remove_handler():

    server = Dispatcher()

    handler = lambda x: x

    server.add_handler(handler, 'test')
    server.remove_handler(handler, 'test')

    assert len(server.get_events()) == 0

    with pytest.raises(TypeError):
        server.add_handler('test', 'not_a_handler')

    with pytest.raises(TypeError):
        server.remove_handler('test', 'not_a_handler')
