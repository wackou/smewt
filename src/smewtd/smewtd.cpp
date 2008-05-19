#include <QSettings>
#include <QList>
#include <QDebug>
#include "smewtd.h"
#include "dljob.h"
#include "../smewtexception.h"
using namespace smewt;


Smewtd::Smewtd(QApplication *app) : QDBusAbstractAdaptor(app), _app(app) {
  connect(app, SIGNAL(aboutToQuit()), SIGNAL(aboutToQuit()));

  settings = new Settings(app);
  _storage = new StorageProxy(settings->storageDomain, this);
}

Smewtd::~Smewtd() {
  delete settings;
  delete _storage;
}

bool Smewtd::ping() {
  return true;
}

void Smewtd::quit() {
  _app->quit();
}

void Smewtd::query(QString query) {
  _storage->query(query);
}

QStringList Smewtd::queryMovies() {
  return _storage->queryMovies();
}

QStringList Smewtd::queryLucene(const QString& queryString) {
  return _storage->queryLucene(queryString);
}

void Smewtd::distantQueryLucene(const QString& host, const QString& queryString) {
  _storage->distantQueryLucene(host, queryString);
}

Friend Smewtd::getFriend(const QString& friendName) const {
  for (int i=0; i<settings->friends.size(); i++) {
    if (settings->friends[i].name == friendName) {
      return settings->friends[i];
    }
  }
  throw SmewtException(QString("cannot get friend") + friendName);
}

void Smewtd::startDownload(QString friendName, QString filename) {
  Q_ASSERT(filename.left(7) == "file://");

  Friend source = getFriend(friendName);
  QString sftpAddress = QString("sftp://") + source.ip + filename.right(filename.size()-7);

  // todo implement me
  QString localAddress = settings->incomingFolder + "/" + sftpAddress.split("/").back();

  qDebug() << "starting download from: " << sftpAddress << "to:" << localAddress;

  DownloadJob* dljob = new DownloadJob(sftpAddress, localAddress, source.userpwd);

  dljob->start();
  
}

#include "smewtd.moc"
