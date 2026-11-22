import {loadFont as loadInter} from '@remotion/google-fonts/Inter';
import {loadFont as loadGrotesk} from '@remotion/google-fonts/SpaceGrotesk';
import {loadFont as loadDeva} from '@remotion/google-fonts/NotoSansDevanagari';

// Devanagari falls back to Noto Sans Devanagari so Hindi text renders on any machine.
const deva = loadDeva().fontFamily;
export const fonts = {body: `${loadInter().fontFamily}, ${deva}`, display: `${loadGrotesk().fontFamily}, ${deva}`, deva};

// Channel A design tokens: one background, one accent, one support colour.
export const C = {
  bg: '#0B1020',
  bgGlow: '#16213D',
  land: '#26314F',
  landEdge: '#3A4870',
  grid: 'rgba(140,160,210,0.16)',
  text: '#F4F6FB',
  muted: '#8E9AB8',
  accent: '#FFB547',   // the thing we are talking about
  second: '#3DD6C6',   // the thing we compare it with
  third: '#9AA8FF',    // everything else named in the video
};
export const colorFor = (i: number) => (i === 0 ? C.accent : C.second);

// One colour per named place for the whole video: first named = accent,
// second = support, everything else = third.
import React from 'react';
export const ColorCtx = React.createContext<Record<string, string>>({});
export function buildColorMap(scenes: {props: any}[]): Record<string, string> {
  const order: string[] = [];
  const add = (n: any) => { if (typeof n === 'string' && !order.includes(n)) order.push(n); };
  for (const sc of scenes) {
    const p = sc.props || {};
    [...(p.shapes || []), ...(p.highlight || []), ...((p.fills || []).map((x: any) => (typeof x === 'string' ? x : x.name))),
     ...((p.bars || []).map((b: any) => b[0])), p.shape, p.land_on].forEach(add);
  }
  const map: Record<string, string> = {};
  order.forEach((n, i) => { map[n] = i === 0 ? C.accent : i === 1 ? C.second : C.third; });
  return map;
}
export const useColor = () => { const m = React.useContext(ColorCtx); return (n: string, i = 0) => m[n] || colorFor(i); };
