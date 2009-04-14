/*
 * Smewt - A smart collection manager
 * Copyright (c) 2008 Nicolas Wack
 *
 * Smewt is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * Smewt is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 */


#include "storageproxy.h"
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
#include <QDebug>
#include "smewtd.h"
using namespace Soprano;
using namespace smewt;


#define horizontalBar QString(100, '-').toUtf8().data()

void StorageProxy::connect(const QString& service) {
  Client::DBusClient* client = new Client::DBusClient(service);

  /*
  qDebug() << "Available models:";
  qDebug() << "-----------------";
  qDebug() << client->allModels() << endl;
  */

  qDebug() << "Connecting to main model";
  _model = client->createModel("main");

  if (!_model) {
    qDebug() << "Connection failed...";
  }
  else {
    qDebug() << "success!";
  }

}

QList<QueryResult> StorageProxy::query(const QString& queryString) {
  qDebug() << horizontalBar;
  QList<BindingSet> bresults = executeSparqlQuery(queryString);
  int nrows = bresults.size();
  qDebug() << "got" << nrows << "results";
  
  QList<QueryResult> results;

  for (int i=0; i<nrows; i++) {
    QueryResult qresult;
    if (results.empty()) {
      foreach (QString bindingName, bresults[i].bindingNames()) {
	qresult << bindingName;
      }
      results << qresult;
      qresult.clear();
    }
    foreach (QString name, bresults[i].bindingNames()) {
      qresult << bresults[i][name].toString();
    }
    results << qresult;
  }
  
  return results;
}

QList<BindingSet> StorageProxy::executeSparqlQuery(const QString& queryString) {
  qDebug() << "Doing SPARQL search:" << queryString;
  Soprano::QueryResultIterator it
    = _model->executeQuery(niceify(queryString), Query::QueryLanguageSparql);
  qDebug() << "OK, fetching results...";

  bool tryFaster = false;
  if (tryFaster) {
    //return a QList<QueryResult> already, using code like that:
    //int ncols = it.bindingCount();
    //QStringList bnames = it.bindingNames();
    // iterate instead of asking allBindings at once
    return it.allBindings();
  }

  return it.allBindings();
}

QString StorageProxy::niceify(const QString& queryString) const {
  QString prefix
    = QString("PREFIX nao: <%1> "
	      "PREFIX rdfs: <%2> "
	      "PREFIX xls: <%3> "
	      "PREFIX xesam: <%4> ")
    .arg(Soprano::Vocabulary::NAO::naoNamespace().toString())
    .arg("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    .arg(Soprano::Vocabulary::XMLSchema::xsdNamespace().toString())
    .arg(Soprano::Vocabulary::Xesam::xesamNamespace().toString());

  return prefix + queryString;
}


StorageProxy::StorageProxy(const QString& service, Smewtd* smewtd) : _smewtd(smewtd) {
  connect(service);
}


QStringList StorageProxy::queryMovies() {
  qDebug() << horizontalBar;
  QList<QueryResult> results = query("select distinct ?filename where { ?filename rdfs:type xesam:File } limit 10");

  QStringList movies;
  int fidx = 0;
  for (int i=0; i<results[0].size(); i++) {
    if (results[0][i] == "filename") fidx = i;
  }
  for (int i=1; i<results.size(); i++) {
    QString filename = results[i][fidx];
    if (filename.endsWith(".avi")) {
      movies << filename;
    }
  }

  qDebug() << "found following movies:" << movies;
  qDebug() << horizontalBar;

  return movies;
}


QStringList StorageProxy::queryLucene(const QString& queryString) {
  qDebug() << horizontalBar;
  qDebug() << "Doing lucene search on:" << queryString;
  Soprano::QueryResultIterator it =
    _model->executeQuery(queryString,
			 Soprano::Query::QueryLanguageUser,
			 "lucene");

  qDebug() << "  results:";
  QStringList results;
  while (it.next()) {
    QUrl resource = it.binding( "resource" ).uri();
    double score = it.binding( "score" ).literal().toDouble();

    results << resource.toString();
    qDebug() << "  " << resource << score;
  }
  qDebug() << horizontalBar;

  return results;
}
