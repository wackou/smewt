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
