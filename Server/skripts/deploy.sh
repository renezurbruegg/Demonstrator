#!/bin/bash
SKRIPTPATH="$PWD/$(dirname $0)"
# Create a temporary directory and store its name in a variable ...
TMPDIR=$(mktemp -d)

# Bail out if the temp directory wasn't created successfully.
#if [ -e $TMPDIR ]; then
 #   >&2 echo "Failed to create temp directory"
  #  exit 1
#fi

echo $TMPDIR
#echo $pwd
#cd $TMPDIR
#touch file
#cd $TMPDIR
#ls -l "$TMPDIR"
# Make sure it gets removed even if the script exits abnormally.
#trap "exit 1"           HUP INT PIPE QUIT TERM
#trap 'rm -rf "$TMPDIR"' EXIT

# Example use of TMPDIR:
echo "unzipping"
FILENAME=$(ls -t $SKRIPTPATH/../front/dist | head -1)
unzip  $SKRIPTPATH/../front/dist/$FILENAME -d $TMPDIR
folder=$(ls -t $TMPDIR | head -1)
cp -r $TMPDIR/$folder/* /var/www/html
