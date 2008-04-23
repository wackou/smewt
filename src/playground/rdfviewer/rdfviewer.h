#include <QMainWindow>
#include <QTableWidget>

class RDFViewer : public QMainWindow {
  Q_OBJECT

 protected:
  QTableWidget* _table;

 public:

  RDFViewer();
};

