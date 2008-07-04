#!/usr/bin/python

from collections import defaultdict



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
            # @todo change this to an exception
            assert(value is None or type(value) == self.schema[key])

        defaultdict.__setitem__(self, key, value)


# @todo isn't it better to implement properties as actual python properties? or attributes?
# @todo write unit tests for this class...
class MediaObject:

    # need to be defined in plugins

    # 1- 'typename' which is a string representing the type name
    
    # 2- 'schema' which is a dictionary from property name to type
    # ex: schema = { 'epNumber': int,
    #                'title': str
    #                }

    # 3- 'converters', which is a dictionary from property name to
    #    a function that is able to parse this property from a string

    # 4- 'unique' which is the list of properties that form a primary key

    def __init__(self, dictionary = {}, headers = [], row = []):
        # create the properties
        self.properties = ValidatingSmewtDict(self.schema)
        self.confidence = SmewtDict(self.schema)
        
        #for prop in self.schema:
        #    self.properties[prop] = None
        
        if dictionary:
            self.readFromDict(dictionary)

        if headers and row:
            self.readFromRow(headers, row)
        

    # used to make sure the values correspond to the schema
    def isValid(self):
        # compare properties' type
        try:
            for prop in self.schema.keys():
                if self.properties[prop] is not None and type(self.properties[prop]) != self.schema[prop]:
                    return False
        except KeyError:
            return False
        
        return True

        
    def __repr__(self):
        return self.typename + '(' + repr(self.properties) + ')'

    # check this function still works correctly
    def __str__(self):
        result = ('valid ' if self.isValid() else 'invalid ') + self.typename + ':\n{ '
        for key, value in self.properties.items():
            result += '%-10s : %s\n  ' % (key, str(value))
        return result + '}'

    def keys(self):
        return self.properties.keys()

    def getAttributes(self, attrs):
        result = [ self[attr] for attr in attrs ]
        return tuple(result)

    def getUniqueKey(self):
        return self.getAttributes(self.unique)


    def __getitem__(self, prop):
        return self.properties[prop]

    def __setitem__(self, prop, value):
        self.properties[prop] = value

    #def setValue(self,

    @staticmethod
    def parse(cls, name, value):
        if name not in cls.schema:
            return value
        
        if name in cls.converters:
            # types that need a specific conversion
            return cls.converters[name](value)
                    
        else:
            # otherwise just call the default constructor
            return cls.schema[name](value)

    def parseProperty(self, name, value):
        return self.parse(self, name, value)
        

    def readFromDict(self, d):
        for prop, value in d.items():
            self.properties[prop] = self.parseProperty(prop, value)

    def readFromRow(self, headers, row):
        '''giving too much information in the row is not a problem,
        extra fields will be ignored'''
        # OR
        '''if a key from the headers is not in the schema, error because
        the user could have misspelt it'''
        # ?

        for prop, value in zip(headers, row):
            try:
                self.properties[prop] = self.parseProperty(prop, value)
                
            except KeyError:
                # property name is not in the schema
                pass
