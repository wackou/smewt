#include <QApplication>
#include <QtDBus/QDBusConnection>
#include "smewtd.h"
using namespace smewt;


#define SERVICE_NAME "com.smewt.Smewt"
void registerDBusObjects(Smewtd* smewtd);


int main(int argc, char *argv[]) {
  QApplication app(argc, argv);
  app.setOrganizationName("DigitalGaia");
  app.setOrganizationDomain("smewt.com");
  app.setApplicationName("Smewt");

  Smewtd* smewtd = new Smewtd(&app);

  registerDBusObjects(smewtd);

  return app.exec();
}


void registerDBusObjects(Smewtd* smewtd) {
  QDBusConnection sbus = QDBusConnection::sessionBus();

  // register main service
  if (!sbus.registerService(SERVICE_NAME)) {
    throw SmewtException("Could not register DBus service: ", SERVICE_NAME);
  }

  // register smewtd object
  if (!sbus.registerObject("/Smewtd", smewtd,
			   QDBusConnection::ExportAllSlots | QDBusConnection::ExportAllProperties)) {
    throw SmewtException("Could not register Smewtd DBus object");
  }

  // register settings object
  if (!sbus.registerObject("/Settings", smewtd->settings,
			   QDBusConnection::ExportAllSlots | QDBusConnection::ExportAllProperties)) {
    throw SmewtException("Could not register Settings DBbus object");
  }

  qDebug() << "DBus registration successful!";
}
