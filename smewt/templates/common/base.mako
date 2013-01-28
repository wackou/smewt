<%!
from smewt.base.utils import smewtMedia, smewtMediaUrl

def media(filename):
    return smewtMediaUrl('common', filename)

%>

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

	<link rel="stylesheet" href="/static/css/style.css">
	<script src="/static/js/libs/modernizr-2.6.1-respond-1.1.0.min.js"></script>
</head>
<body>


${next.body()}


<script src="/static/js/libs/jquery-1.8.1.min.js"></script>
<script src="/static/js/libs/bootstrap.min.js"></script>

<script src="/static/js/script.js"></script>

<%block name="scripts"/>

</body>
</html>
