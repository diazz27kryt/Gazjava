#!/usr/bin/env bash
# Starts a real Minecraft 1.21.11 dedicated server with the mod (via Loom's runServer) and checks:
#  - the mod initialises and registers 3 drinks,
#  - no recipe / resource parsing errors mention gazjava,
#  - every drink exists and carries the consumable, food and use_remainder components
#    (checked over RCON by tools/rcon_check.py).
# Run from the repository root. Needs network access (Minecraft server jar download).
set -uo pipefail

LOG="run/smoke.log"

mkdir -p run
echo "eula=true" > run/eula.txt
cat > run/server.properties <<'EOF'
online-mode=false
level-type=minecraft\:flat
generate-structures=false
spawn-protection=0
view-distance=4
simulation-distance=4
enable-rcon=true
rcon.port=25575
rcon.password=gazjava-smoke
broadcast-rcon-to-ops=false
EOF
rm -f "$LOG"

./gradlew runServer --no-daemon --console=plain < /dev/null > "$LOG" 2>&1 &
SERVER_PID=$!

started=0
for _ in $(seq 1 240); do
  if grep -q 'Done (' "$LOG" 2>/dev/null; then started=1; break; fi
  if ! kill -0 "$SERVER_PID" 2>/dev/null; then break; fi
  sleep 2
done

fail=0
if [ "$started" -eq 1 ]; then
  python3 -I tools/rcon_check.py || fail=1
else
  echo "FAIL: server did not finish starting"
  fail=1
fi

# give the server up to 90s to shut down (rcon_check sends "stop"), then make sure nothing is left
for _ in $(seq 1 45); do
  kill -0 "$SERVER_PID" 2>/dev/null || break
  sleep 2
done
kill "$SERVER_PID" 2>/dev/null || true

echo "------ tail of server log ------"
tail -n 40 "$LOG"
echo "--------------------------------"

if grep -q 'GazJava loaded: 3 drinks registered' "$LOG"; then
  echo "PASS: mod initialised with 3 drinks"
else
  echo "FAIL: mod did not report 3 registered drinks"
  fail=1
fi

grep -E 'Loaded [0-9]+ recipes' "$LOG" || true

if grep -iE '(parsing error|couldn.t parse|failed to load|missing).*gazjava|gazjava.*(parsing error|couldn.t parse|failed to load|unknown)' "$LOG"; then
  echo "FAIL: gazjava related errors found in the log"
  fail=1
else
  echo "PASS: no gazjava related errors in the log"
fi

exit "$fail"
