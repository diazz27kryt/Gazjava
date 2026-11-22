#!/usr/bin/env bash
# Starts a real Minecraft 1.21.11 dedicated server with the mod (via Loom's runServer) and checks:
#  - the mod initialises and registers 3 drinks,
#  - no recipe / resource parsing errors mention gazjava,
#  - every drink exists and carries the consumable, food and use_remainder components.
# Run from the repository root. Needs network access (Minecraft server jar download).
set -uo pipefail

LOG="run/smoke.log"
FIFO="$(mktemp -u /tmp/gazjava-stdin.XXXXXX)"
DRINKS=(gazyava_nefora gazyava_ofnika gazyava_motobrata)

mkdir -p run
echo "eula=true" > run/eula.txt
cat > run/server.properties <<'EOF'
online-mode=false
level-type=minecraft\:flat
generate-structures=false
spawn-protection=0
view-distance=4
simulation-distance=4
EOF
rm -f "$LOG"
mkfifo "$FIFO"
exec 3<>"$FIFO"

send() { echo "$1" >&3; sleep "${2:-1}"; }

./gradlew runServer --no-daemon --console=plain <&3 > "$LOG" 2>&1 &
SERVER_PID=$!

started=0
for _ in $(seq 1 240); do
  if grep -q 'Done (' "$LOG" 2>/dev/null; then started=1; break; fi
  if ! kill -0 "$SERVER_PID" 2>/dev/null; then break; fi
  sleep 2
done

if [ "$started" -eq 1 ]; then
  send "forceload add 0 0" 4
  send "setblock 0 100 0 minecraft:chest" 2
  for d in "${DRINKS[@]}"; do
    send "item replace block 0 100 0 container.0 with gazjava:$d" 1
    for comp in consumable food use_remainder; do
      send "execute if items block 0 100 0 container.0 gazjava:$d[minecraft:$comp] run say SMOKE_OK $d $comp" 1
    done
  done
  send "stop" 1
fi

# give the server up to 90s to shut down, then make sure nothing is left running
for _ in $(seq 1 45); do
  kill -0 "$SERVER_PID" 2>/dev/null || break
  sleep 2
done
kill "$SERVER_PID" 2>/dev/null || true
exec 3>&-
rm -f "$FIFO"

echo "------ tail of server log ------"
tail -n 60 "$LOG"
echo "--------------------------------"

fail=0
check() { # description, grep-pattern
  if grep -qE "$2" "$LOG"; then echo "PASS: $1"; else echo "FAIL: $1"; fail=1; fi
}

if [ "$started" -ne 1 ]; then echo "FAIL: server did not finish starting"; exit 1; fi

check "mod initialised with 3 drinks" 'GazJava loaded: 3 drinks registered'
for d in "${DRINKS[@]}"; do
  for comp in consumable food use_remainder; do
    check "$d has $comp" "SMOKE_OK $d $comp"
  done
done

if grep -iE '(parsing error|couldn.t parse|failed to load|missing).*gazjava|gazjava.*(parsing error|couldn.t parse|failed to load|unknown)' "$LOG"; then
  echo "FAIL: gazjava related errors found in the log"
  fail=1
else
  echo "PASS: no gazjava related errors in the log"
fi

exit "$fail"
