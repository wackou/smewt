#include <QSettings>
#include <QList>
#include <QDebug>
#include "smewtd.h"
using namespace smewt;


void Smewtd::readConfig() {
  reset();

  QSettings settings;
  qDebug("Loading config");
  friends[0].name = settings.value("friend0/name", friends[0].name).toString();
  friends[0].ip = settings.value("friend0/ip", friends[0].ip).toString();
  friends[1].name = settings.value("friend1/name", friends[1].name).toString();
  friends[1].ip = settings.value("friend1/ip", friends[1].ip).toString();

}


void Smewtd::saveConfig() {
  QSettings settings;
  qDebug("Saving config");
  settings.setValue("friend0/name", friends[0].name);
  settings.setValue("friend0/ip", friends[0].ip);
  settings.setValue("friend1/name", friends[1].name);
  settings.setValue("friend1/ip", friends[1].ip);
  settings.setValue("friends/number", 100);
}

void Smewtd::reset() {
  qDebug("resetting");
  friends.clear();
  friends << Friend() << Friend();

  friends[0].name = "Wackou";
  friends[0].ip = "192.168.1.2";

  friends[1].name = "Ricard";
  friends[1].ip = "192.168.1.2";
  
}


int Smewtd::test() {
  return 23;
}

void Smewtd::quit() {
}

void Smewtd::startDownload(QString friendName, QString filename) {
  Q_ASSERT(filename.left(7) == "file://");

  QString friendIp;

  for (int i=0; i<friends.size(); i++) {
    if (friends[i].name == friendName) {
      friendIp = friends[i].ip;
    }
  }

  QString sftpAddress = QString("sftp://") + friendIp + filename.right(filename.size()-7);
  qDebug() << "starting download from: " << sftpAddress;

  
}
