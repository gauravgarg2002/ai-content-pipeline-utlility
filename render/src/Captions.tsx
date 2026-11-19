import React, {useMemo} from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {C, fonts} from './theme';

export type Word = {text: string; startMs: number; endMs: number};

// Groups of up to 3 words; a pause over 250 ms starts a new group.
function group(words: Word[]): Word[][] {
  const out: Word[][] = [];
  for (const w of words) {
    const g = out[out.length - 1];
    if (!g || g.length >= 3 || w.startMs - g[g.length - 1].endMs > 250) out.push([w]); else g.push(w);
  }
  return out;
}

export const Captions: React.FC<{words: Word[]}> = ({words}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const ms = (f / fps) * 1000;
  const groups = useMemo(() => group(words), [words]);
  const g = groups.find((x, i) => ms >= x[0].startMs - 60 && ms < (groups[i + 1]?.[0].startMs ?? x[x.length - 1].endMs + 400) - 60);
  if (!g) return null;
  return (
    <div style={{position: 'absolute', top: 1440, left: 70, right: 150, display: 'flex', justifyContent: 'center'}}>
      <div style={{background: 'rgba(8,12,24,0.72)', borderRadius: 22, padding: '14px 26px',
        fontFamily: fonts.body, fontWeight: 800, fontSize: 70, lineHeight: 1.1, textAlign: 'center', color: C.text}}>
        {g.map((w, i) => (
          <span key={i} style={{color: ms >= w.startMs && ms < w.endMs + 80 ? C.accent : C.text}}>
            {w.text}{i < g.length - 1 ? ' ' : ''}
          </span>
        ))}
      </div>
    </div>
  );
};
