#ifndef STORAGEPROXY_H
#define STORAGEPROXY_H

#include <Soprano/Model>
#include <Soprano/QueryResultIterator>
#include <Soprano/StatementIterator>
#include <QList>

namespace smewt {

class Smewtd;

class StorageProxy {
  Soprano::Model* _model;
  Smewtd* _smewtd;

  QList<Soprano::BindingSet> executeSparqlQuery(const QString& queryString);

 public:
  StorageProxy(const QString& service, Smewtd* smewtd);


  QString niceify(const QString& queryString) const;
  void connect(const QString& service);
  void query(const QString& queryString);

  QStringList queryMovies();
  QStringList queryLucene(const QString& queryString);

  void distantQueryLucene(const QString& host, const QString& queryString);
};

} // namespace smewt


#endif // STORAGEPROXY_H
