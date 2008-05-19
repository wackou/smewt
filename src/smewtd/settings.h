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

#define DEFINE_PROPERTY(type, propertyName)                            \
  type propertyName;                                                   \
  type get_##propertyName() const { return propertyName; }             \
  void set_##propertyName(const type& value) { propertyName = value; }

class Settings : public QDBusAbstractAdaptor {

  Q_OBJECT

  Q_CLASSINFO("D-Bus Interface", "com.smewt.Smewt.Settings");
  Q_PROPERTY(QString organizationName READ organizationName);
  Q_PROPERTY(QString organizationDomain READ organizationDomain);

  //Q_PROPERTY(QString friends READ get_friends WRITE set_friends);
  Q_PROPERTY(QString incomingFolder READ get_incomingFolder WRITE set_incomingFolder);
  Q_PROPERTY(QString storageDomain READ get_storageDomain WRITE set_storageDomain);
  Q_PROPERTY(QString idKey READ get_idKey WRITE set_idKey);

  QApplication* _app;

 public:

  Settings(QApplication *app);
  ~Settings();

  // Config property list
  DEFINE_PROPERTY(QList<Friend>, friends);
  DEFINE_PROPERTY(QString, incomingFolder);
  DEFINE_PROPERTY(QString, storageDomain);
  DEFINE_PROPERTY(QString, idKey);


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
