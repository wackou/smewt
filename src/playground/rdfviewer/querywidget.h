#include <Soprano/Model>
#include <QTableWidget>
#include <QPushButton>
#include <QLineEdit>
#include <QWidget>
#include <QTextEdit>

class QueryWidget : public QWidget {
  Q_OBJECT

 protected:

  QLineEdit* _queryText;
  QPushButton* _queryButton;
  QTableWidget* _table;
  Soprano::Model* _model;

 public:
  QueryWidget();


  QString niceify(const QString& queryString) const;
  void connect();
  void query(const QString& queryString);

 public slots:
  void newQuery();

};

