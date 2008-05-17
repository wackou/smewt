#ifndef SMEWTEXCEPTION_H
#define SMEWTEXCEPTION_H

#include <QString>
#include <QStringList>
#include <QTextStream>
#include <exception>


namespace smewt {

/**
 * Exception class that can take up to 3 arguments of any type, which will
 * be serialized into a QString for the error message.
 */
class SmewtException : public std::exception {
 protected:
  QString _msg;
  mutable QByteArray _message;

 public:
  SmewtException(const QString& msg) : _msg(msg) {}
  SmewtException(const char* msg) : _msg(msg) {}
  SmewtException(const std::string& msg) : _msg(QString::fromStdString(msg)) {}
  SmewtException(const QStringList& msg) : _msg(msg.join("")) {}

  template <typename T, typename U>
  SmewtException(const T& a, const U& b) {
    QTextStream(&_msg) << a << b;
  }

  template <typename T, typename U, typename V>
  SmewtException(const T& a, const U& b, const V& c) {
    QTextStream(&_msg) << a << b << c;
  }

  virtual ~SmewtException() throw() {}
  virtual const char* what() const throw() {
    // NB: we need to store the ascii message permanently inside the exception
    // instance, otherwise it gets destroyed when we come out and the pointer is
    // invalid
    _message = _msg.toUtf8();

    return _message.data();
  }

  const QString& msg() const throw () { return _msg; }
};



/**
 * Use this define to creates derived instances of SmewtException easily.
 */
#define SMEWT_DEFINE_EXCEPTION(UserException)                                   \
class UserException : public SmewtException {                                   \
 public:                                                                        \
  UserException(const QString& msg) : SmewtException(msg) {}                    \
  UserException(const char* msg) : SmewtException(msg) {}                       \
  UserException(const std::string& msg) : SmewtException(msg) {}                \
  UserException(const QStringList& msg) : SmewtException(msg) {}                \
  template <typename T, typename U>                                             \
  UserException(const T& a, const U& b) : SmewtException(a, b) {}               \
  template <typename T, typename U, typename V>                                 \
  UserException(const T& a, const U& b, const V& c) : SmewtException(a, b, c) {}\
};

} // namespace smewt


#endif // SMEWTEXCEPTION_H
