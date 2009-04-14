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


#include <QDebug>
#include "dljob.h"


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
  qDebug() << "Starting dl thread";
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
