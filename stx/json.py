import json


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        d = getattr(obj, '__dict__', None)

        if d is not None:
            d = dict(d)
            d.update({'__type__': obj.__class__.__name__})
            return d

        if isinstance(obj, set):
            return list(obj)

        return json.JSONEncoder.default(self, obj)


def dumps(obj, *, indent=None):
    return json.dumps(obj, cls=CustomEncoder, indent=indent)
