#include <QApplication>
#include "rdfviewer.h"

int main(int argc, char* argv[]) {
  QApplication app(argc, argv);

  RDFViewer mainWindow("org.kde.NepomukStorage");
  mainWindow.show();

  return app.exec();
}
