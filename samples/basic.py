#!/usr/bin/env python3.5

import asyncio
import json
import time

from async_dispatch import Dispatcher, SubscriberInterface, PublisherInterface, Event


class BasicPublisher(PublisherInterface):

    count = 0

    async def produce(self):
        cls = self.__class__
        cls.count += 1
        v = cls.count

        return Event('test', time.time(), json.dumps({'value':v}))


class BasicSubscriber(SubscriberInterface):

    listen_to_events = ['test']

    def __init__(self):

        self.total = 0

    async def consume(self, event):

        event_name, timestamp, payload = event
        payload = json.loads(payload)
        self.total += int(payload['value'])

    def get_total(self):

        return self.total

if __name__ == '__main__':

    publisher = BasicPublisher()
    subscriber = BasicSubscriber()

    loop = asyncio.get_event_loop()

    server = Dispatcher(publisher, subscriber, loop=loop)
    loop.run_until_complete(server.start(max_events=5))

    total = subscriber.get_total()
    print("Total is %d" % total)

    assert total == 15

