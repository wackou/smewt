#!/usr/bin/python

# @todo isn't it better to implement properties as actual python properties? or attributes?
class MediaObject:

    # need to be defined in plugins

    # 1- 'typename' which is a string representing the type name
    
    # 2- 'schema' which is a dictionary from property name to type
    # ex: schema = { 'epNumber': int,
    #                'title': str
    #                }

    # 3- 'converters', which is a dictionary from property name to
    #    a function that is able to parse this property from a string

    def __init__(self, headers = [], row = []):
        # create the properties
        self.property = {}
        for prop in self.schema:
            self.property[prop] = None

        self.readFromRow(headers, row)
        

    # used to make sure the values correspond to the schema
    def isValid(self):
        # compare number of attributes
        if len(self.property) != len(self.schema):
            return False

        # compare properties' type
        try:
            for prop in self.schema.keys():
                if self.property[prop] is not None and type(self.property[prop]) != self.schema[prop]:
                    return False
        except KeyError:
            return False
        
        return True

    '''
    def __getattr__(self, name):
        print 'getattr', name
        # @todo this looks old-style classes...
        # convert to new style? (doesn\'t to work now...)
        # see http://docs.python.org/ref/attribute-access.html
        try:
            p = self.__dict__['property'] # self.property
            print 'got p'
            if name in p:
                return p[name]
            else: raise AttributeError, name
        except KeyError:
            raise AttributeError, name

    def __setattr__(self, name, value):
        try:
            d = self.__dict__
            print 'ooh'
            props = d['property']
            print 'ah'
            if name in self.__dict__['property']:
                self.__dict__['property'][name] = value
            else: raise AttributeError, name
        except KeyError:
            print 'oooh'
            raise AttributeError, name
    '''
        
    def __repr__(self):
        return self.typename + '(' + repr(self.property) + ')'

    def __str__(self):
        result = self.typename + ':\n{ '
        for key, value in self.property.items():
            result += '%-10s : %s\n  ' % (key, str(value))
        return result + '}'

    def __setitem__(self, prop, value):
        self.property[prop] = value

    def readFromRow(self, headers, row):
        '''giving too much information in the row is not a problems,
        extra fields will be ignored'''
        # OR
        '''if a key from the headers is not in the schema, error because
        the user could have misspelt it'''
        # ?

        for prop, value in zip(headers, row):
            try:
                p = self.schema[prop]
                
                if prop in self.converters:
                    # types that need a specific conversion
                    self.property[prop] = self.converters[prop](value)
                    
                else:
                    # otherwise just call the default constructor
                    self.property[prop] = self.schema[prop](value)
                    
            except KeyError:
                # property name is not in the schema
                pass
