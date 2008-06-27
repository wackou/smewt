#include <QList>
#include <QDebug>
#include "smewtd.h"
#include "dljob.h"
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


QDBusVariant Smewtd::query(const QString& host, const QString& queryString) {
  QList<QVariant> results;
  QList<QueryResult> qresults;

  // is "if (host) {" correct?
  if (host == "") {
    qresults = _storage->query(queryString);
  }
  else {
    // perform distant query
  }

  for (int i=0; i<qresults.size(); i++) {
    results << QVariant(qresults[i]);
  }
  return QDBusVariant(results);
}

QStringList Smewtd::queryMovies() {
  return _storage->queryMovies();
}

QStringList Smewtd::queryLucene(const QString& queryString) {
  return _storage->queryLucene(queryString);
}

void Smewtd::distantQueryLucene(const QString& host, const QString& queryString) {
  QString cmd = QString("qdbus \"com.smewt.Smewt\" \"/\" \"queryLucene\" \"%1\"").arg(queryString);
  QString shell = QString("ssh -i %1 %2  DISPLAY=:0 ")
    .arg(settings->idKey)
    .arg(getFriend(host).ip);

  qDebug() << "executing remote query:" << shell + cmd;
  QProcess distantQuery;
  distantQuery.start(shell + cmd);
  if (!distantQuery.waitForFinished()) {
    return;
  }

  QByteArray result = distantQuery.readAll();
  qDebug() << result;
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
  QString localAddress = settings->incomingFolder + "/" + sftpAddress.split("/").back();

  qDebug() << "starting download from: " << sftpAddress << "to:" << localAddress;

  DownloadJob* dljob = new DownloadJob(sftpAddress, localAddress, source.userpwd);

  dljob->start();
  
}

#include "smewtd.moc"
