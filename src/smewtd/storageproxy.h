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


#ifndef STORAGEPROXY_H
#define STORAGEPROXY_H

#include <Soprano/Model>
#include <Soprano/QueryResultIterator>
#include <Soprano/StatementIterator>
#include <QList>

namespace smewt {

class Smewtd;

typedef QList<QString> QueryResult;

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
