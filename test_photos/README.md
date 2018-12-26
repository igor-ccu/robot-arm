This is a comment to myself:

Rename files by using guid generator:
Get-ChildItem . |% {mv $_.name "$([guid]::NewGuid().ToString()+$_.extension)"}
