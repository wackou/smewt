/*
 * Smewt - A smart collection manager
 * Copyright (c) 2008 Nicolas Wack
 *
 * Smewt is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * Smewt is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 */


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
