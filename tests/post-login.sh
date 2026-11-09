#!/usr/bin/env bash
# Manual test of login-limit rule in firewall.
# Run 100 requests to login route one per second
# then run one more control request.
# Usage:
#   tests/post-login.sh 100; tests/post-login.sh

BASE_URL=https://pearlx-api-2091523486.us-east-2.elb.amazonaws.com
URL=$BASE_URL/api/v1/auth/login
NUM=${1:-1}
if [[ $NUM = 1 ]]; then
  curl -v -d '{}' -H "Content-type: application/json" $URL
else
  for i in $(seq 1 $NUM); do
    curl -s -S -d '{}' -H "Content-type: application/json" $URL >/dev/null
    echo $i
    sleep 1
  done
fi
