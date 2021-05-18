def print_event(event, args):
    print(f'Event \'{Event.get_event_name(event)}\' ({event}) called with args: {args}')

class Event:
    current_event_code = -1
    _callbacks = []
    _callback_names = {}

    @staticmethod
    def get_event_code(name: str = '', verbose: bool = False):
        Event.current_event_code += 1

        Event._callback_names[Event.current_event_code] = name

        if verbose:
            Event.register(Event.current_event_code, print_event)

        return Event.current_event_code

    @staticmethod
    def get_event_name(event_code: int):
        if event_code in Event._callback_names:
            return Event._callback_names[event_code]
        return ''

    @staticmethod
    def dispatch(event, **args):
        for key, callback in Event._callbacks:
            if event == key:
                callback(event, args)

    @staticmethod
    def register(key, callback: callable):
        Event._callbacks.append((key, callback))

    @staticmethod
    def unregister(key: int = None, callback: callable = None):
        Event._callbacks = [(k, cb) for k, cb in Event._callbacks if not ((cb == callback or cb == None) and (k == key or k == None))]

    @staticmethod
    def clear():
        Event._callbacks = []