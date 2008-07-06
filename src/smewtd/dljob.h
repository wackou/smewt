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


#ifndef DLJOB_H
#define DLJOB_H

#include <QApplication>
#include <QFont>
#include <QPushButton>
#include <QVBoxLayout>
#include <QWidget>
#include <QThread>
#include <QObject>
#include <curl/curl.h>


class DownloadJob : public QThread {
  Q_OBJECT

 public:
  DownloadJob(const QString& remoteURL, const QString& localURL, const QString& userpwd);

  void run();

  void emitUpdate(int value);

  void setMaximum(int value) { _maxValue = value; _maximumSet = true; }

  signals: //slots
  void updateProgress(int value);

 public:
  QString _remote, _local, _userpwd;

 protected:
  int _maxValue;
  bool _maximumSet;
};

#endif // DLJOB_H
