#ifndef DLWIDGET_H
#define DLWIDGET_H

#include <QApplication>
#include <QFont>
#include <QPushButton>
#include <QProgressBar>
#include <QVBoxLayout>
#include <QWidget>
#include <QThread>
#include <QObject>
#include <curl/curl.h>



class DownloadWidget : public QWidget {
  Q_OBJECT

 public:
  DownloadWidget(QWidget *parent = 0);

 public slots:
  void startDownload();

 protected:
  QProgressBar* _pbar;

};

#endif // DLWIDGET_H
