#ifndef DLJOB_H
#define DLJOB_H

#include <QApplication>
#include <QFont>
#include <QPushButton>
#include <QProgressBar>
#include <QVBoxLayout>
#include <QWidget>
#include <QThread>
#include <QObject>
#include <curl/curl.h>


class DownloadJob : public QThread {
  Q_OBJECT

 public:
  DownloadJob(const QString& remoteURL, const QString& localURL, const QString& userpwd,
	      QProgressBar* pbar);

  void run();

  void emitUpdate(int value);

  void setMaximum(int value) { _pbar->setMaximum(value); }

  signals: //slots
  void updateProgress(int value);

 protected:
  QString _remote, _local, _userpwd;
  QProgressBar* _pbar;
  bool _maximumSet;
};

#endif // DLJOB_H
