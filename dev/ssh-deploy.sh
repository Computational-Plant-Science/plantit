#!/bin/sh

eval "$(ssh-agent -s)" # Start ssh-agent cache
chmod 600 id_rsa # Allow read access to the private key
ssh-add id_rsa # Add the private key to SSH

ssh @USER@$HOST -p $PORT <<EOF
  cd $DIRECTORY
  ./dev/deploy.sh $HOST
EOF