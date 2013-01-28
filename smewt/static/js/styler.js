function toggleByName( whatName )
{
  var x = document.getElementsByName( whatName );

  for(i = 0; i < x.length; i++){
    x[i].style.display = (x[i].style.display=='none') ? 'inline' : 'none';
  }
}

function isToggled( whatName )
{
  var x = document.getElementsByName( whatName );

  if (x[0].style.display == 'inline')
      return true;
  else
      return false;
}
