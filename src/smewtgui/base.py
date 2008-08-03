
class SmewtDict(defaultdict):
    def __init__(self, schema):
        defaultdict.__init__(self, lambda x: None)
        self.schema = schema

    def __missing__(self, key):
        #if not key in self.schema:
        #    raise KeyError
        return None


class ValidatingSmewtDict(SmewtDict):
    def __init__(self, schema):
        super(ValidatingSmewtDict, self).__init__(schema)

    def __setitem__(self, key, value):
        if key in self.schema:
            # TODO: change this to an exception
            assert(value is None or type(value) == self.schema[key])

        defaultdict.__setitem__(self, key, value)
