<%!
from smewt.base.utils import smewtMedia, smewtMediaUrl

def media(filename):
    return smewtMediaUrl('common', filename)

logfile = open('/tmp/makolog.txt', 'w')
logfile.write('-'*100)
logfile.flush()

%>

<%def name="log(*args)">
<%
    if args:
        logfile.write(args[0])
        for msg in args[1:]:
            logfile.write(' ' + str(msg))
    logfile.write('\n')
    logfile.flush()
%>
</%def>

<!doctype html>
<html class="no-js" lang="en">
<head>
	<meta charset="utf-8">
	<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">

	<title></title>
	<meta name="description" content="">
	<meta name="author" content="">

	<meta name="viewport" content="width=device-width">

	<!-- Use SimpLESS (Win/Linux/Mac) or LESS.app (Mac) to compile your .less files
	to style.css, and replace the 2 lines above by this one:
	<link rel="stylesheet/less" href="${smewtMedia('common', 'less/style.less')}">
	<script src="${media('js/libs/less-1.3.0.min.js')}"></script>
	 -->

	<link rel="stylesheet" href="${media('css/style.css')}">

	<script src="${media('js/libs/modernizr-2.5.3-respond-1.1.0.min.js')}"></script>
</head>
<body>


${next.body()}


<script src="//ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js"></script>
<script>window.jQuery || document.write('<script src="${media('js/libs/jquery-1.7.2.min.js')}"><\/script>')</script>

<script src="${media('js/libs/bootstrap/bootstrap.min.js')}"></script>

<script src="${media('js/script.js')}"></script>

<%block name="scripts"/>

</body>
</html>
