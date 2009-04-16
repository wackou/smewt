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


#include <QSettings>
#include <QList>
#include <QDebug>
#include "settings.h"
#include "../smewtexception.h"
using namespace smewt;


Settings::Settings(QApplication *app) : QDBusAbstractAdaptor(app), _app(app) {
  //connect(app, SIGNAL(aboutToQuit()), SIGNAL(aboutToQuit()));

  loadConfig();
}

Settings::~Settings() {
  saveConfig();
}

void Settings::loadConfig() {
  resetConfig();

  QSettings settings;
  qDebug("Loading config");
  friends[0].name = settings.value("friend0/name", friends[0].name).toString();
  friends[0].ip = settings.value("friend0/ip", friends[0].ip).toString();
  friends[0].userpwd = settings.value("friend0/userpwd", friends[0].userpwd).toString();
  friends[1].name = settings.value("friend1/name", friends[1].name).toString();
  friends[1].ip = settings.value("friend1/ip", friends[1].ip).toString();
  friends[1].userpwd = settings.value("friend1/userpwd", friends[1].userpwd).toString();

  incomingFolder = settings.value("folders/incoming", incomingFolder).toString();
  storageDomain = settings.value("general/storagedomain", storageDomain).toString();
  idKey = settings.value("general/idKey", idKey).toString();
}


void Settings::saveConfig() {
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
  settings.setValue("general/storagedomain", storageDomain);
  settings.setValue("general/idKey", idKey);
}

void Settings::resetConfig() {
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

  storageDomain = "org.kde.NepomukStorage";
  idKey = "~/.ssh/smewt_id_dsa";
}


Friend Settings::getFriend(const QString& friendName) const {
  for (int i=0; i<friends.size(); i++) {
    if (friends[i].name == friendName) {
      return friends[i];
    }
  }
  throw SmewtException(QString("cannot get friend") + friendName);
}


#include "settings.moc"
