#include "rdfviewer.h"
#include "querywidget.h"


RDFViewer::RDFViewer() {
  setCentralWidget(new QueryWidget());
  setMinimumSize(1000, 800);
}

