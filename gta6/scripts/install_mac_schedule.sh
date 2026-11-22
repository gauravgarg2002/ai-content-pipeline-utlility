#!/bin/bash
# Runs `python -m pipeline auto` every 20 minutes via launchd (macOS's built-in scheduler).
# Install:   bash scripts/install_mac_schedule.sh
# Uninstall: launchctl unload ~/Library/LaunchAgents/com.gaurav.gta6.plist && rm ~/Library/LaunchAgents/com.gaurav.gta6.plist
# Logs:      gta6/logs/auto.log
set -e
DIR="$(cd "$(dirname "$0")/.." && pwd)"
PY="$DIR/.venv/bin/python"
[ -x "$PY" ] || { echo "Create the venv first: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"; exit 1; }
[ -f "$DIR/.env" ] || { echo "Create $DIR/.env first (see .env.example)"; exit 1; }
mkdir -p "$DIR/logs" ~/Library/LaunchAgents
PLIST=~/Library/LaunchAgents/com.gaurav.gta6.plist
cat > "$PLIST" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.gaurav.gta6</string>
  <key>WorkingDirectory</key><string>$DIR</string>
  <key>ProgramArguments</key><array>
    <string>/usr/bin/caffeinate</string><string>-i</string>
    <string>$PY</string><string>-m</string><string>pipeline</string><string>auto</string>
  </array>
  <key>EnvironmentVariables</key><dict>
    <key>PATH</key><string>$DIR/.venv/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
  </dict>
  <key>StartInterval</key><integer>1200</integer>
  <key>RunAtLoad</key><true/>
  <key>StandardOutPath</key><string>$DIR/logs/auto.log</string>
  <key>StandardErrorPath</key><string>$DIR/logs/auto.log</string>
</dict></plist>
PL
launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"
echo "Scheduled: every 20 min. Logs: $DIR/logs/auto.log"
