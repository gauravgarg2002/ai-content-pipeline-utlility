import React from 'react';
import {interpolate, spring, useCurrentFrame, useVideoConfig, Easing} from 'remotion';
import {geoCircle, geoGraticule10} from 'd3-geo';
import {C, colorFor, fonts} from '../theme';
import {ATLANTIC, geoCentroid, land, mercatorFor, pathFor, shape, trueSize} from '../geo';

export type SceneP = {p: any; onScreen: string | null; d: number; first: boolean};

const W = 1080, H = 1920;
const useSpring = (delay = 0, first = false) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  return first ? 1 : spring({frame: f - delay, fps, config: {damping: 16, stiffness: 120}});
};
const Svg: React.FC<{children: React.ReactNode}> = ({children}) => (
  <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{position: 'absolute', inset: 0}}>{children}</svg>
);
const Label: React.FC<{x: number; y: number; text: string; color: string; size?: number; o?: number}> = ({x, y, text, color, size = 44, o = 1}) => (
  <text x={x} y={y} textAnchor="middle" fontFamily={fonts.display} fontWeight={700} fontSize={size} fill={color}
    opacity={o} style={{paintOrder: 'stroke', stroke: C.bg, strokeWidth: 10}}>{text.toUpperCase()}</text>
);

const WorldBase: React.FC<{grid?: boolean}> = ({grid}) => {
  const path = pathFor(mercatorFor(ATLANTIC));
  return (<>
    {grid ? <path d={path(geoGraticule10()) || ''} fill="none" stroke={C.grid} strokeWidth={1.5} /> : null}
    <path d={path(land) || ''} fill={C.land} stroke={C.landEdge} strokeWidth={1.2} />
  </>);
};

// Countries highlighted on the real (Mercator) map.
const MercatorHighlight: React.FC<SceneP> = ({p, first}) => {
  const proj = mercatorFor(ATLANTIC); const path = pathFor(proj);
  const names: string[] = p.shapes || p.highlight || [];
  return (<Svg><WorldBase grid />
    {names.map((n, i) => { const s = useSpring(i * 8, first); const f = shape(n); const [x, y] = proj(geoCentroid(f)) || [0, 0];
      return (<g key={n}><path d={path(f) || ''} fill={colorFor(i)} fillOpacity={0.85 * s} stroke={colorFor(i)} strokeWidth={3} />
        <Label x={x} y={y} text={n} color={C.text} o={s} /></g>); })}
  </Svg>);
};

// Shapes side by side at true relative size.
const TrueSizeStack: React.FC<SceneP> = ({p, first}) => {
  const names: string[] = p.shapes || [];
  const slotH = 820 / names.length, scale = p.scale || 560;
  return (<Svg>{names.map((n, i) => { const s = useSpring(i * 10, first); const cy = 520 + slotH * (i + 0.5);
    return (<g key={n} opacity={s}><path d={trueSize(shape(n), scale, W / 2, cy)} fill={colorFor(i)} fillOpacity={0.85} stroke={colorFor(i)} strokeWidth={3} />
      <Label x={W / 2} y={cy - slotH / 2 + 30} text={n} color={C.text} /></g>); })}</Svg>);
};

const ComparisonSplit: React.FC<SceneP> = (a) => (a.p.projection && a.p.projection !== 'mercator' ? <TrueSizeStack {...a} /> : <MercatorHighlight {...a} />);

const fmt = (v: number) => (v >= 1000 ? Math.round(v).toLocaleString('en-US') : String(Math.round(v * 100) / 100));
const BarCompare: React.FC<SceneP> = ({p, first}) => {
  const f = useCurrentFrame(); const bars: [string, number][] = p.bars || [];
  const max = Math.max(...bars.map((b) => b[1])); const unit = p.unit ? ` ${p.unit}` : '';
  return (<Svg>{bars.map(([name, v], i) => {
    const s = useSpring(6 + i * 10, first); const y = 640 + i * 230; const w = 880 * (v / max) * s;
    const shown = interpolate(f, [6 + i * 10, 30 + i * 10], [0, v], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
    return (<g key={name}>
      <text x={100} y={y - 24} fontFamily={fonts.display} fontWeight={700} fontSize={48} fill={C.text}>{name.toUpperCase()}</text>
      <rect x={100} y={y} width={Math.max(w, 8)} height={120} rx={18} fill={colorFor(i)} />
      <text x={100 + Math.max(w, 8) + 20} y={y + 82} fontFamily={fonts.display} fontWeight={700} fontSize={56}
        fill={colorFor(i)}>{first ? fmt(v) : fmt(shown)}{unit}</text>
    </g>); })}</Svg>);
};

const KineticText: React.FC<SceneP> = ({p, onScreen, first}) => {
  const text: string = p.text || onScreen || '';
  return (<Svg>{text.split(' ').map((w, i, arr) => { const s = useSpring(i * 4, first);
    return (<text key={i} x={W / 2} y={820 + (i - (arr.length - 1) / 2) * 150} textAnchor="middle" fontFamily={fonts.display}
      fontWeight={700} fontSize={140} fill={i === arr.length - 1 ? C.accent : C.text} opacity={s}
      transform={`translate(0 ${(1 - s) * 60})`}>{w}</text>); })}</Svg>);
};

// Smaller countries packed inside a container, all at true size.
const PACK: Record<string, [number, number]> = {USA: [-20, -250], China: [70, 40], India: [130, 320]};
const ShapePack: React.FC<SceneP> = ({p, first}) => {
  const scale = 760, cx = W / 2, cy = 900;
  const pieces: string[] = p.pieces || [];
  return (<Svg>
    <path d={trueSize(shape(p.container), scale, cx, cy)} fill="none" stroke={C.second} strokeWidth={5} strokeDasharray="14 10" />
    <Label x={cx - 300} y={cy + 470} text={p.container} color={C.second} />
    {pieces.map((n, i) => { const s = useSpring(10 + i * 14, first); const [dx, dy] = PACK[n] || [0, (i - 1) * 260];
      return (<g key={n} opacity={s} transform={`translate(0 ${(1 - s) * 500})`}>
        <path d={trueSize(shape(n), scale, cx + dx, cy + dy)} fill={C.accent} fillOpacity={0.8} stroke={C.bg} strokeWidth={3} />
        <Label x={cx + dx} y={cy + dy + 14} text={n} color={C.text} size={40} /></g>); })}
  </Svg>);
};

// Mercator graticule with equal-size circles that balloon toward the poles.
const GridStretch: React.FC<SceneP> = ({p, first}) => {
  const proj = mercatorFor(ATLANTIC); const path = pathFor(proj);
  const lats = [0, 30, 50, 65, 75], lons = [-60, -30, 0, 30, 60];
  const hl: string[] = p.highlight || [];
  return (<Svg><WorldBase grid />
    {hl.map((n, i) => <path key={n} d={path(shape(n)) || ''} fill={colorFor(i)} fillOpacity={0.55} />)}
    {lats.map((lat, li) => lons.map((lon) => { const s = useSpring(li * 6, first);
      return <path key={`${lat}${lon}`} d={path(geoCircle().center([lon, lat]).radius(4.5 * Math.max(s, 0.01))()) || ''}
        fill="rgba(255,255,255,0.12)" stroke={C.text} strokeWidth={2.5} />; }))}
  </Svg>);
};

// Slide a country toward the equator on Mercator and watch it shrink.
const DragShape: React.FC<SceneP> = ({p, d}) => {
  const f = useCurrentFrame();
  const target = shape(p.land_on || 'Africa'); const mover = shape(p.shape || 'Greenland');
  const [lonG, latG] = geoCentroid(mover); const [lonT] = geoCentroid(target);
  const t = interpolate(f, [8, d * 0.8], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const latNow = latG + ((p.to_lat ?? 0) - latG) * t; const lonNow = lonG + (lonT - lonG) * t;
  const base = mercatorFor(ATLANTIC); const moving = mercatorFor(ATLANTIC, lonNow, [-lonG, latNow - latG]);
  const [lx, ly] = moving([0, 0]) || [0, 0];
  return (<Svg><WorldBase />
    <path d={pathFor(base)(target) || ''} fill={C.second} fillOpacity={0.35} stroke={C.second} strokeWidth={3} />
    <path d={pathFor(moving)(mover) || ''} fill={C.accent} fillOpacity={0.9} stroke={C.bg} strokeWidth={2} />
    <Label x={lx} y={ly + 16} text={p.shape || 'Greenland'} color={C.text} size={40} />
  </Svg>);
};

export const Fallback: React.FC<SceneP> = (a) => <KineticText {...a} p={{text: a.onScreen || ''}} />;

export const SCENES: Record<string, React.FC<SceneP>> = {
  comparison_split: ComparisonSplit, bar_compare: BarCompare, kinetic_text: KineticText,
  shape_pack: ShapePack, grid_stretch: GridStretch, drag_shape: DragShape, map_highlight: MercatorHighlight,
};
