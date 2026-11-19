#!/usr/bin/env bash
# Confirms both secrets work without printing them.
set -u
ok=0
code=$(curl -s -o /tmp/gm.json -w '%{http_code}' "https://generativelanguage.googleapis.com/v1beta/models?key=${GEMINI_API_KEY}")
if [ "$code" = "200" ]; then
  n=$(python3 -c "import json;print(sum('flash' in m['name'] for m in json.load(open('/tmp/gm.json'))['models']))")
  echo "| GEMINI_API_KEY | OK | $n Flash models visible |" >> "$GITHUB_STEP_SUMMARY"
else
  echo "| GEMINI_API_KEY | FAILED | HTTP $code |" >> "$GITHUB_STEP_SUMMARY"; ok=1
fi
code=$(curl -s -o /tmp/hf.json -w '%{http_code}' -H "Authorization: Bearer ${HF_TOKEN}" https://huggingface.co/api/whoami-v2)
if [ "$code" = "200" ]; then
  role=$(python3 -c "import json;d=json.load(open('/tmp/hf.json'));print(d.get('auth',{}).get('accessToken',{}).get('role','?'))")
  echo "| HF_TOKEN | OK | token role: $role |" >> "$GITHUB_STEP_SUMMARY"
else
  echo "| HF_TOKEN | FAILED | HTTP $code |" >> "$GITHUB_STEP_SUMMARY"; ok=1
fi
exit $ok
