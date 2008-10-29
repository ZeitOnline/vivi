#!/bin/bash
# This is a fake publish script which is used by the tests.

tmpfile=`mktemp`

cat > $tmpfile

echo Publishing test script
cat $tmpfile
echo

grep JPG $tmpfile > /dev/null
ret=$?

rm $tmpfile

if [ "$ret" -eq "0" ]; then
    echo "error" >&2
    exit 1
fi

echo "done."
