import {loadFont as loadInter} from '@remotion/google-fonts/Inter';
import {loadFont as loadGrotesk} from '@remotion/google-fonts/SpaceGrotesk';

export const fonts = {body: loadInter().fontFamily, display: loadGrotesk().fontFamily};

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
};
export const colorFor = (i: number) => (i === 0 ? C.accent : C.second);
