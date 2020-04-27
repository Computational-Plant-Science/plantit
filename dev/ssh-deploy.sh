#!/bin/sh

eval "$(ssh-agent -s)" # Start ssh-agent cache
chmod 600 id_rsa # Allow read access to the private key
ssh-add id_rsa # Add the private key to SSH

ssh -o $SSH_USER@$SSH_HOST -p $SSH_PORT <<EOF
  cd $SSH_DIRECTORY
  ./dev/deploy.sh $SSH_HOST
EOF