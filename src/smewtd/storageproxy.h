#ifndef STORAGEPROXY_H
#define STORAGEPROXY_H

#include <Soprano/Model>
#include <Soprano/QueryResultIterator>
#include <Soprano/StatementIterator>
#include <QList>

namespace smewt {

class Smewtd;

typedef QMap<QString, QString> QueryResult;

class StorageProxy {
  Soprano::Model* _model;
  Smewtd* _smewtd;

  QList<Soprano::BindingSet> executeSparqlQuery(const QString& queryString);

 public:
  StorageProxy(const QString& service, Smewtd* smewtd);
  void connect(const QString& service);

  // generic SPARQL query function
  QList<QueryResult> query(const QString& queryString);

  // specific queries
  QStringList queryMovies();
  QStringList queryLucene(const QString& queryString);

  // utility function to allow nicer queries
  QString niceify(const QString& queryString) const;

};

} // namespace smewt


#endif // STORAGEPROXY_H
