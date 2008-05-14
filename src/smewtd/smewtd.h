#ifndef SMEWTD_H
#define SMEWTD_H

#include <QApplication>
#include <QStringList>
#include <QtDBus>
#include <QDBusAbstractAdaptor>

namespace smewt {

class Friend {
 public:
  QString name;
  QString ip;
  QString userpwd;
};

class Smewtd : public QDBusAbstractAdaptor {

  Q_OBJECT
  Q_CLASSINFO("D-Bus Interface", "com.smewt.Smewt.Smewtd")
  Q_PROPERTY(QString organizationName READ organizationName)
  Q_PROPERTY(QString organizationDomain READ organizationDomain)


 protected:
  QApplication* _app;

  Friend getFriend(const QString& friendName) const;

 public:

  // Config property list
  QList<Friend> friends;
  QString incomingFolder;


  Smewtd(QApplication *app) : QDBusAbstractAdaptor(app), _app(app) {
    connect(app, SIGNAL(aboutToQuit()), SIGNAL(aboutToQuit()));

    readConfig();
  }

  ~Smewtd() {
    saveConfig();
  }

  void readConfig();
  void saveConfig();

 public:

  QString organizationName() {
    return _app->organizationName();
  }

  QString organizationDomain() {
    return _app->organizationDomain();
  }

 public slots:
  void reset();
  
  int test();

  void startDownload(QString friendName, QString filename);

  Q_NOREPLY void quit();

 signals:
  void aboutToQuit();
};

} // namespace smewt

#endif // SMEWTD_H
