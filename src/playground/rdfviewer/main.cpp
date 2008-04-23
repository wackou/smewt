#include <QApplication>
#include "rdfviewer.h"

int main(int argc, char* argv[]) {
  QApplication app(argc, argv);

  RDFViewer mainWindow;
  mainWindow.show();

  return app.exec();
}
