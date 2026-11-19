#!/usr/bin/env bash
# Join beat wavs with a gap, normalise loudness, export mp3. Usage: mix.sh <dir> <out.mp3>
set -euo pipefail
dir=$1; out=$2
gap=$(python3 -c "import json;print(json.load(open('config/voices.json'))['mix']['beat_gap_s'])")
lufs=$(python3 -c "import json;print(json.load(open('config/voices.json'))['mix']['loudness_lufs'])")
tp=$(python3 -c "import json;print(json.load(open('config/voices.json'))['mix']['true_peak_db'])")
rate=$(ffprobe -v error -show_entries stream=sample_rate -of csv=p=0 "$(ls "$dir"/b*.wav | head -1)")
ffmpeg -v error -y -f lavfi -i "anullsrc=r=${rate}:cl=mono" -t "$gap" "$dir/_gap.wav"
: > "$dir/_list.txt"
for f in $(ls "$dir"/b*.wav | sort); do
  ffmpeg -v error -y -i "$f" -ar "$rate" -ac 1 -sample_fmt s16 "$f.n.wav"
  echo "file '$(basename "$f").n.wav'" >> "$dir/_list.txt"; echo "file '_gap.wav'" >> "$dir/_list.txt"
done
ffmpeg -v error -y -f concat -safe 0 -i "$dir/_list.txt" -af "loudnorm=I=${lufs}:TP=${tp}:LRA=11" -ar 44100 -b:a 160k "$out"
echo "$(basename "$out"): $(ffprobe -v error -show_entries format=duration -of csv=p=0 "$out" | awk '{printf "%d:%02d", $1/60, $1%60}')" | tee -a "${GITHUB_STEP_SUMMARY:-/dev/null}"
