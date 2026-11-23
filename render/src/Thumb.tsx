import React from 'react';
import {AbsoluteFill, Freeze} from 'remotion';
import {Short, ShortProps} from './Short';

// Thumbnail: one frozen frame of the video itself, with a big text overlay.
// props.thumb = {scene, at (0-1 inside that scene), text ("*word*" = highlight, \n = line), sub?}
export type ThumbProps = ShortProps & {thumb: {scene: number; at?: number; text: string; sub?: string}};

const STYLE: Record<string, {fg: string; hl: string; band: string; font: string}> = {
  'a-maps-data': {fg: '#FFFFFF', hl: '#FFB547', band: 'rgba(11,16,32,0.78)', font: 'Space Grotesk, Inter, sans-serif'},
  'b-ai-hinglish': {fg: '#FFFFFF', hl: '#FFD400', band: 'rgba(8,10,20,0.8)', font: 'Inter, Space Grotesk, sans-serif'},
  'c-horror-hi': {fg: '#F2F2F2', hl: '#E5202A', band: 'rgba(0,0,0,0.55)', font: 'Noto Sans Devanagari, Inter, sans-serif'},
  'd-epics-en': {fg: '#FFF3D6', hl: '#FFB547', band: 'rgba(42,18,6,0.82)', font: 'Space Grotesk, Inter, sans-serif'},
};

const Line: React.FC<{s: string; hl: string}> = ({s, hl}) => (
  <div>{s.split(/(\*[^*]+\*)/).map((part, i) => part.startsWith('*')
    ? <span key={i} style={{color: hl}}>{part.slice(1, -1)}</span> : <span key={i}>{part}</span>)}</div>
);

export const Thumb: React.FC<ThumbProps> = (props) => {
  const {thumb, scenes, width, height, channel} = props;
  const sc = scenes[Math.min(thumb.scene, scenes.length - 1)] || scenes[0];
  const frame = sc ? sc.from + Math.round((thumb.at ?? 0.6) * (sc.durationInFrames - 1)) : 0;
  const clean = {...props, captions: false, audio: '', words: [], scenes: scenes.map((s) => ({...s, onScreen: null}))};
  const st = STYLE[channel] || STYLE['a-maps-data'];
  const portrait = height > width;
  const lines = thumb.text.split('\n');
  const fs = portrait ? (lines.length > 2 ? 122 : 140) : (lines.length > 2 ? 104 : 124);
  return (
    <AbsoluteFill>
      <Freeze frame={frame}><Short {...clean} /></Freeze>
      <AbsoluteFill style={{background: portrait
        ? 'linear-gradient(180deg, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0) 45%)'
        : 'linear-gradient(90deg, rgba(0,0,0,0.6) 0%, rgba(0,0,0,0) 62%)'}} />
      <div style={{position: 'absolute', left: portrait ? 60 : 70, right: portrait ? 60 : width * 0.42, top: portrait ? 150 : undefined,
        bottom: portrait ? undefined : 90, fontFamily: st.font, fontWeight: 800, fontSize: fs, lineHeight: 1.04, color: st.fg,
        letterSpacing: -1, textTransform: channel === 'c-horror-hi' ? 'none' : 'uppercase',
        textShadow: '0 6px 0 rgba(0,0,0,0.55), 0 0 30px rgba(0,0,0,0.6)'}}>
        <div style={{background: st.band, padding: portrait ? '28px 34px' : '26px 34px', borderRadius: 18, display: 'inline-block'}}>
          {lines.map((l, i) => <Line key={i} s={l} hl={st.hl} />)}
          {thumb.sub ? <div style={{fontSize: fs * 0.36, fontWeight: 700, marginTop: 14, color: st.hl, letterSpacing: 2}}>{thumb.sub}</div> : null}
        </div>
      </div>
    </AbsoluteFill>
  );
};
