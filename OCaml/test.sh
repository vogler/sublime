msg=$(echo "hallo lala")
ret=$?

if [[ $ret -ne 1 ]]; then
    echo "fooo!" | nc localhost 9999
fi
