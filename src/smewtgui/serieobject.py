#!/usr/bin/python


from mediaobject import MediaObject

def parseEpisodeList(string):
    # blah
    return []


class SerieObject(MediaObject):

    typename = 'Serie'

    schema = { 'title': str,
               'season': int,
               'episodeList': list
               }

    converters = { 'episodeList': parseEpisodeList }


    def __init__(self):
        MediaObject.__init__(self)

    @staticmethod
    def fromRow(headers, row):
        result = SerieObject()
        MediaObject.readFromRow(result, headers, row)
        return result


class EpisodeObject(MediaObject):

    typename = 'Episode'

    schema = { 'epNumber': int,
               'title': str
               }

    converters = {}

    def __init__(self):
        MediaObject.__init__(self)
            

    @staticmethod
    def fromRow(headers, row):
        result = EpisodeObject()
        MediaObject.readFromRow(result, headers, row)
        return result
