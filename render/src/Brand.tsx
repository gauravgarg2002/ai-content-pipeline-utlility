import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Short} from './Short';

// Channel art: profile picture (square) and banner (16:9, rendered at 1920x1080 and scaled to 2560x1440).
// The background is one of our own scenes, so the art matches the videos.
export type BrandProps = {kind: 'avatar' | 'banner'; channel: string; theme?: string; width: number; height: number; fps: number;
  scene: {type: string; props: any}; frame?: number; name: string; alt?: string; tagline?: string; mark?: string};

const ST: Record<string, {fg: string; hl: string; font: string; band: string}> = {
  'a-maps-data': {fg: '#FFFFFF', hl: '#FFB547', font: 'Space Grotesk, Inter, sans-serif', band: 'rgba(11,16,32,0.72)'},
  'b-ai-hinglish': {fg: '#0B1020', hl: '#FFD400', font: 'Inter, Space Grotesk, sans-serif', band: 'rgba(255,212,0,0.95)'},
  'c-horror-hi': {fg: '#F2F2F2', hl: '#E5202A', font: 'Noto Sans Devanagari, Inter, sans-serif', band: 'rgba(0,0,0,0.5)'},
  'd-epics-en': {fg: '#FFF3D6', hl: '#FFB547', font: 'Space Grotesk, Inter, sans-serif', band: 'rgba(42,18,6,0.8)'},
};

const FIXED = new Set(['puppet', 'atmos']); // scenes drawn on a fixed 1920x1080 stage

export const Brand: React.FC<BrandProps> = (p) => {
  const st = ST[p.channel] || ST['a-maps-data'];
  const fixed = FIXED.has(p.scene.type);
  const dur = 240;
  const short = {id: 'brand', channel: p.channel, fps: p.fps, width: fixed ? 1920 : p.width, height: fixed ? 1080 : p.height, captions: false,
    theme: p.theme, durationInFrames: dur, audio: '', words: [],
    scenes: [{id: 's', type: p.scene.type, props: p.scene.props, onScreen: null, from: 0, durationInFrames: dur}]} as any;
  const cover = fixed ? Math.max(p.width / 1920, p.height / 1080) : 1;
  const bg = fixed
    ? <div style={{position: 'absolute', width: 1920, height: 1080, left: (p.width - 1920 * cover) / 2, top: (p.height - 1080 * cover) / 2,
        transform: `scale(${cover})`, transformOrigin: 'top left'}}><Short {...short} /></div>
    : <Short {...short} />;
  const avatar = p.kind === 'avatar';
  return (
    <AbsoluteFill style={{overflow: 'hidden', background: '#000'}}>
      {bg}
      {avatar ? (
        <AbsoluteFill style={{alignItems: 'center', justifyContent: 'flex-end', paddingBottom: p.height * 0.16}}>
          {p.mark ? <div style={{fontFamily: st.font, fontWeight: 900, fontSize: p.height * 0.2, lineHeight: 1, color: st.fg, background: st.band,
            padding: `${p.height * 0.02}px ${p.height * 0.05}px`, borderRadius: p.height * 0.04, letterSpacing: -2,
            boxShadow: '0 10px 40px rgba(0,0,0,0.5)'}}>{p.mark}</div> : null}
        </AbsoluteFill>
      ) : (
        <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
          {/* YouTube's always-visible safe area is the middle 1546x423 of 2560x1440 = 1160x317 at 1920x1080 */}
          <div style={{width: 1160, height: 317, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
            background: st.band, borderRadius: 24, boxShadow: '0 20px 60px rgba(0,0,0,0.45)'}}>
            <div style={{fontFamily: st.font, fontWeight: 900, fontSize: p.name.length > 16 ? 96 : 118, lineHeight: 1, color: st.fg, letterSpacing: -2}}>{p.name}</div>
            {p.alt ? <div style={{fontFamily: st.font, fontWeight: 700, fontSize: 44, color: st.hl, marginTop: 8}}>{p.alt}</div> : null}
            {p.tagline ? <div style={{fontFamily: 'Inter, sans-serif', fontWeight: 600, fontSize: 34, color: p.channel === 'b-ai-hinglish' ? '#0B1020' : st.hl,
              marginTop: 14, letterSpacing: 1, opacity: 0.95}}>{p.tagline}</div> : null}
          </div>
        </AbsoluteFill>
      )}
    </AbsoluteFill>
  );
};
