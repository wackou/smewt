#ifndef STORAGEPROXY_H
#define STORAGEPROXY_H

#include <Soprano/Model>
#include <Soprano/QueryResultIterator>
#include <Soprano/StatementIterator>
#include <QList>

class StorageProxy {
  Soprano::Model* _model;

  QList<Soprano::BindingSet> executeSparqlQuery(const QString& queryString);

 public:
  StorageProxy(const QString& service);


  QString niceify(const QString& queryString) const;
  void connect(const QString& service);
  void query(const QString& queryString);

  QStringList queryMovies();
  QStringList queryLucene(const QString& queryString);
};

#endif // STORAGEPROXY_H
