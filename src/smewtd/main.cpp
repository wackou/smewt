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

#include "smewtd.h"
using namespace smewt;

int main(int argc, char *argv[]) {
  QApplication app(argc, argv);
  app.setOrganizationName("DigitalGaia");
  app.setOrganizationDomain("smewt.com");
  app.setApplicationName("Smewt");

  Smewtd* smewtd = new Smewtd(&app);

  QDBusConnection sbus = QDBusConnection::sessionBus();

  bool ok = sbus.registerService("com.smewt.Smewt");
  if (ok) {
    qDebug() << "service dbus registration successful!";
  }
  else {
    qDebug() << "could not register dbus service";
    exit(1);
  }


  ok = sbus.registerObject("/Smewtd", smewtd, QDBusConnection::ExportAllSlots | QDBusConnection::ExportAllProperties);
  if (ok) {
    qDebug() << "object dbus registration successful!";
  }
  else {
    qDebug() << "could not register dbus object";
    exit(1);
  }

  ok = sbus.registerObject("/Settings", smewtd->settings, QDBusConnection::ExportAllSlots | QDBusConnection::ExportAllProperties);
  if (ok) {
    qDebug() << "settings dbus registration successful!";
  }
  else {
    qDebug() << "could not register dbus object settings";
    exit(1);
  }

  /*
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
  */


  return app.exec();
}
