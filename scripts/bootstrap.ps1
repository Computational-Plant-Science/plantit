Write-Host "Bootstrapping ${PWD##*/} development environment..."
$compose="docker-compose -f docker-compose.dev.yml"
$nocache=0
$quiet=0

# TODO translate the rest of bootstrap.sh