Get-ChildItem . |% {mv $_.name "$([guid]::NewGuid().ToString()+$_.extension)"}
