#ifndef SMEWTD_H
#define SMEWTD_H

#include <QStringList>
#include <QDBusAbstractAdaptor>
#include "smewtexception.h"
#include "storageproxy.h"
#include "settings.h"

namespace smewt {


class Smewtd : public QDBusAbstractAdaptor {

  Q_OBJECT

  Q_CLASSINFO("D-Bus Interface", "com.smewt.Smewt.Smewtd")
  Q_PROPERTY(QString organizationName READ organizationName)
  Q_PROPERTY(QString organizationDomain READ organizationDomain)


 protected:
  QApplication* _app;
  StorageProxy* _storage;

 public:

  Settings* settings;


  Smewtd(QApplication *app);
  ~Smewtd();

  Friend getFriend(const QString& friendName) const;

  QString organizationName() { return _app->organizationName(); }
  QString organizationDomain() { return _app->organizationDomain(); }

 public slots:
 //void reset();
  
  bool ping();

  void startDownload(QString friendName, QString filename);

  QDBusVariant query(const QString& host, const QString& queryString);
  QStringList queryLucene(const QString& queryString);
  QStringList queryMovies();
  void distantQueryLucene(const QString& host, const QString& queryString);


  Q_NOREPLY void quit();

 signals:
  void aboutToQuit();
};

} // namespace smewt

#endif // SMEWTD_H
