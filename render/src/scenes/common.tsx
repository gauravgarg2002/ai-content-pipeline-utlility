import React from 'react';
import {spring, useCurrentFrame, useVideoConfig, interpolate, Easing} from 'remotion';
import {C, fonts} from '../theme';

export type SceneP = {p: any; onScreen: string | null; d: number; first: boolean};

export const useDims = () => {
  const {width: W, height: H} = useVideoConfig();
  const portrait = H > W;
  const area = portrait ? {x0: 40, y0: 330, x1: W - 40, y1: 1400} : {x0: 90, y0: 170, x1: W - 90, y1: H - 70};
  const k = portrait ? 1 : 0.72; // type scale
  return {W, H, portrait, area, k};
};

export const useSpringAt = (delay = 0, first = false) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  return first && delay <= 0 ? 1 : spring({frame: f - delay, fps, config: {damping: 16, stiffness: 120}});
};

// progress 0..1 across a part of the scene, eased
export const useProgress = (d: number, a = 0, b = 0.75) => {
  const f = useCurrentFrame();
  return interpolate(f, [d * a, Math.max(d * b, d * a + 1)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
};

export const Svg: React.FC<{children: React.ReactNode}> = ({children}) => {
  const {W, H} = useDims();
  return <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{position: 'absolute', inset: 0}}>{children}</svg>;
};

export const Label: React.FC<{x: number; y: number; text: string; color?: string; size?: number; o?: number; anchor?: 'middle' | 'start' | 'end'; upper?: boolean}> =
  ({x, y, text, color = C.text, size = 44, o = 1, anchor = 'middle', upper = true}) => (
    <text x={x} y={y} textAnchor={anchor} fontFamily={fonts.display} fontWeight={700} fontSize={size} fill={color}
      opacity={o} style={{paintOrder: 'stroke', stroke: C.bg, strokeWidth: size / 4.5}}>{upper ? text.toUpperCase() : text}</text>
  );

export const fmtNum = (v: number, decimals?: number) => {
  if (decimals !== undefined) return v.toLocaleString('en-US', {minimumFractionDigits: decimals, maximumFractionDigits: decimals});
  return v >= 1000 ? Math.round(v).toLocaleString('en-US') : String(Math.round(v * 100) / 100);
};
export const decimalsOf = (v: number) => (Number.isInteger(v) ? 0 : String(v).split('.')[1].length);
