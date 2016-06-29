import asyncio
import collections
import logging


Event = collections.namedtuple('Event', ['name', 'ts', 'payload'])


class Dispatcher:
    """
    An event source server.  You can attach publishers and subscribers to the server,
    which will dispatch published Events to the appropriate subscribers.


    """

    def __init__(self, publisher=None, subscribers=None, loop=None, **kwargs):

        if loop is None:
            loop = asyncio.get_event_loop()

        self._loop = loop
        self._subscribers = collections.OrderedDict( )
        self._publishers = None

        if publisher:
            self.add_publisher(publisher)

        # Add a list of subscribers
        if hasattr(subscribers, '__iter__'):
            for subscriber in subscribers:
                self.add_subscriber(subscriber)

    def add_publisher(self, publisher):
        """
        Add a publisher.  A publisher must implement the PublisherInterface.

        :param publisher: PublisherInterface
        :return: self
        """

        if not isinstance(publisher, PublisherInterface):
            raise TypeError('Expects an instance of the PublisherInterface')

        if not getattr(publisher, 'produce') or not callable(publisher.produce):
            raise TypeError('Publishers must implement the produce method()')

        self._publishers = publisher

    def add_subscriber(self, subscriber):
        """
        Add a subscriber.  Each subscriber must report what events it can handle.

        :param subscriber: SubscriberInterface
        :return: self
        """
        if not isinstance(subscriber, SubscriberInterface):
            raise TypeError('Expects an instance of the SubscriberInterface')

        events = subscriber.get_event_listeners()
        t = type(events)
        if t is dict:
            pass
        elif t is list:
            events = {event_name: subscriber.consume for event_name in events}
        else:
            raise TypeError('Cannot determine events from {}'.format(t))

        for event_name, handler in events.items():

            # A string could be the name of the handler
            if isinstance(handler, str) and hasattr(subscriber, handler):
                handler = getattr(subscriber, handler)

            self.add_handler(event_name, handler)

        return self



    def add_handler( self, event_name, handler):
        """
        Add a handler for an event

        :param event_name: Event
        :param handler: Callable method
        :return: Self
        """

        if not callable(handler):
            raise TypeError('Method %r is not callable for event %s' % (handler, event_name))

        if event_name not in self._subscribers:
            self._subscribers[event_name] = []

        self._subscribers[event_name].append(handler)

        return self

    def remove_handler(self, event_name, handler):
        """
        Remove a handler for an event

        :param event_name: string
        :param handler: callable
        :return:
        """

        if not callable(handler):
            raise TypeError('Method %r is not callable for event %s' % (handler, event_name))

        if event_name in self._subscribers:
            items_to_del = []
            for i, h in enumerate(self._subscribers[event_name]):
                if h is handler:
                    items_to_del.append(i)
            for i in items_to_del:
                del self._subscribers[event_name][i]

            # Remove unused events
            if not len(self._subscribers[event_name]):
                del self._subscribers[event_name]

    async def dispatch(self, event):
        """
        Dispatch an event.

        :param event: Event
        :return: mixed
        """

        if not isinstance(event, Event):
            raise TypeError('Expects instance of Event')
        event_name = event.name
        if event_name in self._subscribers:
            for listener in self._subscribers[event_name]:
                logging.debug("Dispatching event %s to subscriber" % event_name)
                result = await listener(event)
                if result and isinstance(result, Event):
                    return result

    async def start(self, max_events=None):
        """Start the server.

        :param max_events: int
        """

        if max_events:
            if type(max_events) is not int:
                raise ValueError("max_events should be an integer")

            if max_events <= 0:
                raise ValueError("max_events must be greater than zero")

        if not self._publishers:
            raise RuntimeError("No publisher provided")

        event = None
        while True:
            if not event:
                event = await self._publishers.produce()
            event = await self.dispatch(event)

            if max_events:
                max_events -= 1

                if max_events <= 0:
                    break


class SubscriberInterface(object):

    listen_to_events = None

    def get_event_listeners(self):

        events = self.__class__.listen_to_events
        if not events:
            raise NotImplementedError()

        return events


class PublisherInterface(object):

    def __next__(self):
        raise NotImplementedError()
