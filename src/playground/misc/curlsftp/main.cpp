#include <QApplication>
#include <QFont>
#include <QPushButton>
#include <QProgressBar>
#include <QVBoxLayout>
#include <QWidget>
#include <QThread>
#include <QObject>
#include <curl/curl.h>

#include "dlwidget.h"


int main(int argc, char *argv[]) {
  QApplication app(argc, argv);
  DownloadWidget widget;
  widget.show();
  return app.exec();
}
