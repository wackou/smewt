#!/usr/bin/python

import dbus


def connect():
    no = dbus.SessionBus().get_object('com.smewt.Smewt', '/')
    return dbus.Interface(no, 'com.smewt.Smewt.Smewtd')


def example():
    server = connect()

    # basic test
    print server.ping()

    # perform a lucene query
    query = 'baraka'
    print 'query lucene: ', query
    
    results = server.queryLucene(query)
    print 'results:'
    for name in results:
        print name


    # download a file
    friend = 'Wackou'
    filename = results[-1]
    print 'start downloading from', friend, ':', filename
    server.startDownload(friend, filename)


if __name__ == '__main__':
    example()
