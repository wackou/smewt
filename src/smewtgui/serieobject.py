#!/usr/bin/python


from mediaobject import MediaObject

def parseEpisodeList(string):
    # blah
    return []


class SerieObject(MediaObject):

    typename = 'Serie'

    schema = { 'title': str,
               'numberSeasons': int,
               'episodeList': list
               }

    unique = [ 'title' ]

    converters = { 'episodeList': parseEpisodeList }



    def __init__(self):
        MediaObject.__init__(self)

    @staticmethod
    def fromDict(d):
        result = SerieObject()
        MediaObject.readFromDict(result, headers, row)
        return result

    @staticmethod
    def fromRow(headers, row):
        result = SerieObject()
        MediaObject.readFromRow(result, headers, row)
        return result


class EpisodeObject(MediaObject):

    typename = 'Episode'

    schema = { 'serie': str,
               'season': int,
               'episodeNumber': int,
               'title': str
               }

    unique = [ 'season', 'episodeNumber' ]

    converters = {}

    def __init__(self):
        MediaObject.__init__(self)

    @staticmethod
    def fromDict(d):
        result = EpisodeObject()
        MediaObject.readFromDict(result, d)
        return result

    @staticmethod
    def fromRow(headers, row):
        result = EpisodeObject()
        MediaObject.readFromRow(result, headers, row)
        return result
