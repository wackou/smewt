#include <QApplication>
#include <QFont>
#include <QPushButton>
#include <QProgressBar>
#include <QVBoxLayout>
#include <QWidget>
#include <QThread>
#include <QObject>
#include <QtDBus/QDBusConnection>
#include <QDebug>
#include <curl/curl.h>
#include <QDBusMessage>
#include <QDBusInterface>

#include "dlwidget.h"
#include "smewtd.h"
using namespace smewt;

int main(int argc, char *argv[]) {
  QApplication app(argc, argv);
  app.setOrganizationName("DigitalGaia");
  app.setOrganizationDomain("smewt.com");
  app.setApplicationName("Smewt");

  DownloadWidget widget;
  Smewtd* smewtd = new Smewtd(&app);

  QDBusConnection sbus = QDBusConnection::sessionBus();

  bool ok = sbus.registerObject("/MainApplication", smewtd);

  if (ok) {
    qDebug() << "dbus registration successful!";
  }
  else {
    qDebug() << "could not register dbus service";
    exit(1);
  }

  smewtd->startDownload("Wackou", "file:///data/Movies/test.avi");

  // dbus test interface
  QDBusInterface* interface = new QDBusInterface("org.freedesktop.DBus",
						 "/",
						 "", 
						 sbus,
						 &app);

  if (!interface->isValid()) {
    qDebug("interface is not valid:");
    qDebug() << interface->lastError().message();
    exit(1);
  }

  QDBusReply<QString> reply = interface->call("GetId");


  if (reply.isValid()) {
    qDebug("reply is valid");
    qDebug() << reply.value();
  }
  else {
    qDebug("invalid reply");
    qDebug() << reply.error().message();
    exit(1);
  }


  // smewt test interface
  /*
  QDBusInterface* sinterface = new QDBusInterface("com.smewt.DBus",
						 "/MainApplication",
						 "",
						 sbus,
						 &app);

  if (!sinterface->isValid()) {
    qDebug("smewt interface is not valid:");
    qDebug() << sinterface->lastError().message();
    exit(1);
  }

  QDBusReply<int> sreply = sinterface->call("test");


  if (sreply.isValid()) {
    qDebug("smewt reply is valid");
    qDebug() << sreply.value();
  }
  else {
    qDebug("smewt invalid reply");
    qDebug() << sreply.error().message();
    exit(1);
  }
  */

  return app.exec();
}
