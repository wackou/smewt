function toggleByName( whatName )
{
  var x = document.getElementsByName( whatName );

  for(i = 0; i < x.length; i++){
    x[i].style.display = (x[i].style.display=='none') ? 'inline' : 'none';
  }
}


