/****************************************************************************
** Meta object code from reading C++ file 'smewtd.h'
**
** Created: Wed May 14 04:12:55 2008
**      by: The Qt Meta Object Compiler version 59 (Qt 4.4.0-rc1)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include "smewtd.h"
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'smewtd.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 59
#error "This file was generated using the moc from 4.4.0-rc1. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
static const uint qt_meta_data_smewt__Smewtd[] = {

 // content:
       1,       // revision
       0,       // classname
       2,   10, // classinfo
       5,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets

 // classinfo: key, value
      30,   14,
      30,   46,

 // signals: signature, parameters, type, tag, flags
      84,   83,   83,   83, 0x05,

 // slots: signature, parameters, type, tag, flags
      98,   83,   83,   83, 0x0a,
     110,   83,  106,   83, 0x0a,
     137,  117,   83,   83, 0x0a,
     178,   83,   83,  168, 0x0a,

       0        // eod
};

static const char qt_meta_stringdata_smewt__Smewtd[] = {
    "smewt::Smewtd\0com.smewt.Smewt\0"
    "D-Bus Interface\0org.freedesktop.DBus.MainApplication\0"
    "\0aboutToQuit()\0reset()\0int\0test()\0"
    "friendName,filename\0startDownload(QString,QString)\0"
    "Q_NOREPLY\0quit()\0"
};

const QMetaObject smewt::Smewtd::staticMetaObject = {
    { &QDBusAbstractAdaptor::staticMetaObject, qt_meta_stringdata_smewt__Smewtd,
      qt_meta_data_smewt__Smewtd, 0 }
};

const QMetaObject *smewt::Smewtd::metaObject() const
{
    return &staticMetaObject;
}

void *smewt::Smewtd::qt_metacast(const char *_clname)
{
    if (!_clname) return 0;
    if (!strcmp(_clname, qt_meta_stringdata_smewt__Smewtd))
	return static_cast<void*>(const_cast< Smewtd*>(this));
    return QDBusAbstractAdaptor::qt_metacast(_clname);
}

int smewt::Smewtd::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QDBusAbstractAdaptor::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        switch (_id) {
        case 0: aboutToQuit(); break;
        case 1: reset(); break;
        case 2: { int _r = test();
            if (_a[0]) *reinterpret_cast< int*>(_a[0]) = _r; }  break;
        case 3: startDownload((*reinterpret_cast< QString(*)>(_a[1])),(*reinterpret_cast< QString(*)>(_a[2]))); break;
        case 4: quit(); break;
        }
        _id -= 5;
    }
    return _id;
}

// SIGNAL 0
void smewt::Smewtd::aboutToQuit()
{
    QMetaObject::activate(this, &staticMetaObject, 0, 0);
}
QT_END_MOC_NAMESPACE
