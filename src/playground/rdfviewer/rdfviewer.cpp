#include "rdfviewer.h"
#include "querywidget.h"


RDFViewer::RDFViewer(const QString& service) {
  setCentralWidget(new QueryWidget(service));
  setMinimumSize(1000, 800);
}

