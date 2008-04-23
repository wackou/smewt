#include "rdfviewer.h"
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
#include <QtCore/QDebug>
using namespace Soprano;


QList<Statement> retrieveStatements() {
  Soprano::Client::DBusClient* client = new Soprano::Client::DBusClient("org.kde.NepomukStorage");
  qDebug() << "Available models:";
  qDebug() << "-----------------";
  qDebug() << client->allModels() << endl;

  qDebug() << "Connecting to main model";
  //Soprano::Client::DBusModel* model = client->createModel("main");
  Soprano::Model* model = client->createModel("main");

  if (!model) {
    qDebug() << "Connection failed...";
    qDebug() << model->lastError();
  }
  else {
    qDebug() << "success!";
  }


  qDebug() << "getting all statements...";
  Soprano::StatementIterator sit = model->listStatements();
  QList<Statement> allStatements = sit.allElements();
  qDebug() << "got" << allStatements.size() << "statements";

  return allStatements;
}



RDFViewer::RDFViewer() {
  QList<Statement> allStatements = retrieveStatements();

  _table = new QTableWidget(allStatements.size(), 3, this);

  int row = 0;
  foreach (Soprano::Statement s, allStatements) {
    _table->setItem(row, 0, new QTableWidgetItem(s.subject().toString()));
    _table->setItem(row, 1, new QTableWidgetItem(s.predicate().toString()));
    _table->setItem(row, 2, new QTableWidgetItem(s.object().toString()));
    row++;
  }
  setCentralWidget(_table);

}

