#include "querywidget.h"
#include <Soprano/Client/DBusClient>
#include <Soprano/Client/DBusModel>
#include <Soprano/QueryResultIterator>
#include <Soprano/Vocabulary/NAO>
#include <Soprano/Vocabulary/Xesam>
#include <Soprano/Vocabulary/RDFS>
#include <Soprano/Vocabulary/XMLSchema>
#include <Soprano/Statement>
#include <Soprano/Model>
#include <Soprano/StatementIterator>
#include <QHeaderView>
#include <QDebug>
#include <QHBoxLayout>
#include <QVBoxLayout>
using namespace Soprano;



void QueryWidget::connect() {
  Soprano::Client::DBusClient* client = new Soprano::Client::DBusClient("org.kde.NepomukStorage");
  qDebug() << "Available models:";
  qDebug() << "-----------------";
  qDebug() << client->allModels() << endl;

  qDebug() << "Connecting to main model";
  //Soprano::Client::DBusModel* model = client->createModel("main");
  _model = client->createModel("main");

  if (!_model) {
    qDebug() << "Connection failed...";
    qDebug() << _model->lastError();
  }
  else {
    qDebug() << "success!";
  }

}

void QueryWidget::query(const QString& queryString) {
  qDebug() << "querying:" << queryString;
  Soprano::QueryResultIterator it
    = _model->executeQuery(queryString, Query::QueryLanguageSparql);
  
  QStringList results;

  int ncols = it.bindingCount();
  _table->setColumnCount(ncols);

  QStringList bnames = it.bindingNames();
  qDebug() << "bnames:" << bnames;
  _table->setHorizontalHeaderLabels(bnames);

  QList<BindingSet> bindings = it.allBindings();
  int nrows = bindings.size();
  _table->setRowCount(nrows);
  qDebug() << "got" << nrows << "results";

  
  int row = 0;
  foreach (BindingSet bset, bindings) {
    for (int col=0; col<ncols; col++) {
      _table->setItem(row, col, new QTableWidgetItem(bset[col].toString()));
    }
    row++;
  }
  /*
  while (it.next()) {
    //Soprano::Node value = it.binding("r");
    Soprano::BindingSet bindings = *it;
    QStringList names = bindings.bindingNames();
    QStringList res;
    foreach (QString name, names) {
      QStringList r;
      r << name << ":" << bindings[name].toString();
      res << r;
    }
    //results << value.toString();
    results << res.join(" || ");
  }
  */

  //_resultText->setText(results.join("\n"));
}


QString QueryWidget::niceify(const QString& queryString) const {
  QString prefix
    = QString("PREFIX nao: <%1> "
	      "PREFIX rdfs: <%2> "
	      "PREFIX xls: <%3> "
	      "PREFIX xesam: <%4> ")
    .arg(Soprano::Vocabulary::NAO::naoNamespace().toString())
    //.arg(Soprano::Vocabulary::RDFS::rdfsNamespace().toString())
    .arg("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    .arg(Soprano::Vocabulary::XMLSchema::xsdNamespace().toString())
    .arg(Soprano::Vocabulary::Xesam::xesamNamespace().toString());

  return prefix + queryString;
}

void QueryWidget::newQuery() {
  QString queryString
    = QString("select ?subject ?predicate ?object "
	      "where { ?subject ?predicate ?object . }");
  if (!_queryText->text().isEmpty()) {
    queryString = _queryText->text();
  }
  query(niceify(queryString));
}

QueryWidget::QueryWidget() {
  _queryText = new QLineEdit();
  _queryButton = new QPushButton("Search now");

  QObject::connect(_queryButton, SIGNAL(clicked()),
		   this, SLOT(newQuery()));

  QHBoxLayout* hlayout = new QHBoxLayout();
  hlayout->addWidget(_queryText);
  hlayout->addWidget(_queryButton);

  connect();

  _table = new QTableWidget(0, 3, this);

  _table->setSelectionMode(QAbstractItemView::NoSelection);
  _table->verticalHeader()->setVisible(false);
  QStringList headers;
  headers << "subject" << "predicate" << "object";
  _table->setHorizontalHeaderLabels(headers);


  QVBoxLayout* vlayout = new QVBoxLayout();
  vlayout->addLayout(hlayout);
  vlayout->addWidget(_table);
  

  setLayout(vlayout);

}

