#!/bin/sh
tabpy-user add -u "$TABPY_USER" -p "$TABPY_PASS" -f /app/pwd.txt || true
tabpy --config /app/tabpy.conf &
until curl -s http://localhost:9004/info > /dev/null; do sleep 2; done
python /app/deploy_cpu.py || echo "Deploy failed"
wait