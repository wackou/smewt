#include "dlwidget.h"
#include "dljob.h"
#include <iostream>
using namespace std;


DownloadWidget::DownloadWidget(QWidget *parent)
  : QWidget(parent) {
  QPushButton* dlbutton = new QPushButton(tr("Download Now"));
  dlbutton->setFont(QFont("Times", 18, QFont::Bold));
  connect(dlbutton, SIGNAL(clicked()), this, SLOT(startDownload()));

  _pbar = new QProgressBar();
  

  QVBoxLayout *layout = new QVBoxLayout;
  layout->addWidget(dlbutton);
  layout->addWidget(_pbar);
  setLayout(layout);
}


void DownloadWidget::startDownload() {
  cout << "starting download" << endl;
  
  DownloadJob* job = new DownloadJob("sftp://192.168.1.4/tmp/test.avi",
				     "/tmp/video.avi",
				     "download:download!", _pbar);

  connect(job, SIGNAL(updateProgress(int)),
	  _pbar, SLOT(setValue(int)));

  job->start();
  cout << "job started" << endl;
}

