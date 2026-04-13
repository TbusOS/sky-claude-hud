#!/bin/bash
# Install claude-hud statusline into Claude Code settings
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SETTINGS="$HOME/.claude/settings.json"
STATUSLINE_CMD="python3 ${SCRIPT_DIR}/statusline.py"

echo "Claude HUD installer"
echo "===================="
echo ""
echo "Statusline command: ${STATUSLINE_CMD}"
echo "Settings file:      ${SETTINGS}"
echo ""

# Test the script works
echo '{"model":{"display_name":"test"},"context_window":{"used_percentage":45},"cost":{"total_cost_usd":0.5,"total_duration_ms":300000}}' \
  | python3 "${SCRIPT_DIR}/statusline.py"
echo ""

if [ ! -f "$SETTINGS" ]; then
    echo "Error: $SETTINGS not found"
    exit 1
fi

# Check if statusLine already configured
if python3 -c "
import json, sys
with open('${SETTINGS}') as f:
    d = json.load(f)
if 'statusLine' in d:
    print('existing: ' + json.dumps(d['statusLine']))
    sys.exit(1)
sys.exit(0)
" 2>/dev/null; then
    # Add statusLine config
    python3 -c "
import json
with open('${SETTINGS}') as f:
    d = json.load(f)
d['statusLine'] = {
    'type': 'command',
    'command': '${STATUSLINE_CMD}'
}
with open('${SETTINGS}', 'w') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
print('Done! statusLine added to settings.json')
print('Restart Claude Code to see the HUD.')
"
else
    echo ""
    echo "statusLine already configured in settings.json."
    echo "To update, manually edit: ${SETTINGS}"
    echo ""
    echo "Expected config:"
    echo "  \"statusLine\": {"
    echo "    \"type\": \"command\","
    echo "    \"command\": \"${STATUSLINE_CMD}\""
    echo "  }"
fi
