#ifndef SMEWT_SETTINGS_H
#define SMEWT_SETTINGS_H

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


class Settings : public QDBusAbstractAdaptor {

  Q_OBJECT

  Q_CLASSINFO("D-Bus Interface", "com.smewt.Smewt.Settings")
  Q_PROPERTY(QString organizationName READ organizationName)
  Q_PROPERTY(QString organizationDomain READ organizationDomain)

  QApplication* _app;

 public:

  // Config property list
  QList<Friend> friends;
  QString incomingFolder;
  QString storageDomain;
  QString idKey;


  Settings(QApplication *app) : QDBusAbstractAdaptor(app), _app(app) {
    //connect(app, SIGNAL(aboutToQuit()), SIGNAL(aboutToQuit()));

    loadConfig();
  }

  ~Settings() {
    saveConfig();
  }

  Friend getFriend(const QString& friendName) const;

  void resetConfig();
  void loadConfig();
  void saveConfig();

 public:

  QString organizationName() {
    return _app->organizationName();
  }

  QString organizationDomain() {
    return _app->organizationDomain();
  }

};

} // namespace smewt

#endif // SMEWT_SETTINGS_H
