#include <QDebug>
#include "dljob.h"
#include <iostream>
using namespace std;

int progress(void* data, double dltotal, double dlnow,
	     double ultotal, double ulnow) {
  DownloadJob* dljob = (DownloadJob*)data;

  dljob->setMaximum((int)dltotal);
  dljob->emitUpdate((int)dlnow);

  if (dlnow >= dltotal) {
    qDebug() << "Finished downloading:" << dljob->_local;
  }

  return 0;
}

void DownloadJob::emitUpdate(int value) {
  emit updateProgress(value);
}


DownloadJob::DownloadJob(const QString& remoteURL, const QString& localURL,
			 const QString& userpwd) :
  _remote(remoteURL), _local(localURL), _userpwd(userpwd),
  _maximumSet(false) {

}


void DownloadJob::run() {
  cout << "Starting dl thread" << endl;
  FILE* fout = fopen(_local.toAscii().data(), "wb");
  CURL* c = curl_easy_init();
  curl_easy_setopt(c, CURLOPT_URL, _remote.toAscii().data());
  //curl_easy_setopt(c, CURLOPT_ERRORBUFFER, errorBuffer);
  curl_easy_setopt(c, CURLOPT_NOPROGRESS, 0);
  curl_easy_setopt(c, CURLOPT_PROGRESSFUNCTION, progress);
  curl_easy_setopt(c, CURLOPT_PROGRESSDATA, this);
  curl_easy_setopt(c, CURLOPT_WRITEDATA, fout);
  curl_easy_setopt(c, CURLOPT_USERPWD, "download:download!");
  int success = curl_easy_perform(c);
  Q_UNUSED(success);
}

#include "dljob.moc"
