#include <QSettings>
#include <QList>
#include <QDebug>
#include "smewtd.h"
#include "dljob.h"
using namespace smewt;


void Smewtd::readConfig() {
  reset();

  QSettings settings;
  qDebug("Loading config");
  friends[0].name = settings.value("friend0/name", friends[0].name).toString();
  friends[0].ip = settings.value("friend0/ip", friends[0].ip).toString();
  friends[0].userpwd = settings.value("friend0/userpwd", friends[0].userpwd).toString();
  friends[1].name = settings.value("friend1/name", friends[1].name).toString();
  friends[1].ip = settings.value("friend1/ip", friends[1].ip).toString();
  friends[1].userpwd = settings.value("friend1/userpwd", friends[1].userpwd).toString();

  incomingFolder = settings.value("folders/incoming", incomingFolder).toString();
}


void Smewtd::saveConfig() {
  QSettings settings;
  qDebug("Saving config");
  settings.setValue("friend0/name", friends[0].name);
  settings.setValue("friend0/ip", friends[0].ip);
  settings.setValue("friend0/userpwd", friends[0].userpwd);
  settings.setValue("friend1/name", friends[1].name);
  settings.setValue("friend1/ip", friends[1].ip);
  settings.setValue("friend1/userpwd", friends[1].userpwd);

  settings.setValue("friends/number", 100);
  settings.setValue("folders/incoming", incomingFolder);
}

void Smewtd::reset() {
  qDebug("resetting");
  friends.clear();
  friends << Friend() << Friend();

  friends[0].name = "Wackou";
  friends[0].ip = "192.168.1.2";
  friends[0].userpwd = "download:download!";

  friends[1].name = "Ricard";
  friends[1].ip = "192.168.1.2";
  friends[1].userpwd = "download:download!";

  incomingFolder = "/tmp";
}


int Smewtd::test() {
  return 23;
}

void Smewtd::quit() {
  _app->quit();
}

Friend Smewtd::getFriend(const QString& friendName) const {
  for (int i=0; i<friends.size(); i++) {
    if (friends[i].name == friendName) {
      return friends[i];
    }
  }
  throw QString("cannot get friend") + friendName;
}

void Smewtd::startDownload(QString friendName, QString filename) {
  Q_ASSERT(filename.left(7) == "file://");

  Friend source = getFriend(friendName);
  QString sftpAddress = QString("sftp://") + source.ip + filename.right(filename.size()-7);

  // todo implement me
  QString localAddress = incomingFolder + "/" + sftpAddress.split("/").back();

  qDebug() << "starting download from: " << sftpAddress << "to:" << localAddress;

  DownloadJob* dljob = new DownloadJob(sftpAddress, localAddress, source.userpwd);

  dljob->start();
  
}
