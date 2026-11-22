// Whole-world scenes: pins on far-flung places, a route between two places,
// count-ups and clocks. Added for "The country with the most time zones".
import React from 'react';
import {interpolate, spring, useCurrentFrame, useVideoConfig, Easing} from 'remotion';
import {geoArea, geoGraticule10, geoInterpolate, geoMercator} from 'd3-geo';
import {C, fonts, useColor} from '../theme';
import {geoCentroid, land, pathFor, shape} from '../geo';
import type {SceneP} from './index';

const W = 1080, H = 1920;
const rad = (d: number) => (d * Math.PI) / 180;
const mercY = (lat: number) => Math.log(Math.tan(Math.PI / 4 + rad(lat) / 2));

// Full 360° Mercator, centred on 10°E so the Pacific islands sit on both edges
// without being cut, and Antarctica's coast is just visible at the bottom.
const LAT_TOP = 75, LAT_BOTTOM = -72, TOP = 560, CENTER_LON = 10;
const S = W / (2 * Math.PI);
export const worldProj = () => geoMercator().scale(S).rotate([-CENTER_LON, 0, 0])
  .translate([W / 2, TOP + S * mercY(LAT_TOP)]).precision(0.2);
const MAP_BOTTOM = TOP + S * (mercY(LAT_TOP) - mercY(LAT_BOTTOM));

// lon, lat of the places our scripts pin. Overseas France: one pin per time zone.
export const PLACES: Record<string, [number, number]> = {
  Paris: [2.35, 48.86], 'Mainland France': [2.35, 46.6],
  'French Polynesia': [-149.4, -17.6], Tahiti: [-149.4, -17.6], Marquesas: [-140.0, -9.0], Gambier: [-134.9, -23.1],
  Clipperton: [-109.2, 10.3], Guadeloupe: [-61.55, 16.25], Martinique: [-61.0, 14.6], 'French Guiana': [-53.1, 3.9],
  'Saint Pierre and Miquelon': [-56.3, 46.9], Mayotte: [45.15, -12.8], Reunion: [55.5, -21.1], Kerguelen: [69.3, -49.3],
  'New Caledonia': [165.6, -21.3], 'Wallis and Futuna': [-176.2, -13.3], 'Adelie Land': [139.0, -68.0],
};

const useSpring = (delay = 0, first = false) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  return first ? 1 : spring({frame: f - delay, fps, config: {damping: 16, stiffness: 120}});
};
const Svg: React.FC<{children: React.ReactNode}> = ({children}) => (
  <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{position: 'absolute', inset: 0}}>
    <defs><clipPath id="mapclip"><rect x={0} y={TOP - 40} width={W} height={MAP_BOTTOM - TOP + 40} /></clipPath></defs>
    {children}
  </svg>
);
const Txt: React.FC<{x: number; y: number; t: string; c: string; s?: number; o?: number; a?: 'start' | 'middle' | 'end'}> =
  ({x, y, t, c, s = 30, o = 1, a = 'middle'}) => (
  <text x={x} y={y} textAnchor={a} fontFamily={fonts.display} fontWeight={700} fontSize={s} fill={c} opacity={o}
    style={{paintOrder: 'stroke', stroke: C.bg, strokeWidth: 8}}>{t}</text>
);

const WorldMap: React.FC = () => {
  const path = pathFor(worldProj());
  return (<g clipPath="url(#mapclip)">
    <path d={path(geoGraticule10()) || ''} fill="none" stroke={C.grid} strokeWidth={1.2} />
    <path d={path(land) || ''} fill={C.land} stroke={C.landEdge} strokeWidth={1} />
  </g>);
};

// Antarctic sector claims are wedges between two meridians, not countries in the atlas.
const SECTORS: Record<string, [number, number]> = {'Adelie Land': [136, 142]};
function sector(name: string): any {
  const [a, b] = SECTORS[name];
  const ring: [number, number][] = [];
  for (let lon = a; lon <= b; lon += 1) ring.push([lon, -60]);
  for (let lon = b; lon >= a; lon -= 1) ring.push([lon, -85]);
  ring.push([a, -60]);
  const f: any = {type: 'Feature', properties: {name}, geometry: {type: 'Polygon', coordinates: [ring]}};
  if (geoArea(f) > 2 * Math.PI) f.geometry.coordinates = [ring.slice().reverse()];  // d3 winding: keep the small side
  return f;
}

type Pin = {name: string; label?: string; dx?: number; dy?: number};
const asPin = (x: string | Pin): Pin => (typeof x === 'string' ? {name: x} : x);

// map_highlight on the whole world: highlighted countries/sectors, optional pins,
// optional strike-through (props.then === "strike").
export const WorldHighlight: React.FC<SceneP> = ({p, d, first}) => {
  const f = useCurrentFrame(); const proj = worldProj(); const path = pathFor(proj); const col = useColor();
  const names: string[] = p.highlight || []; const pins: Pin[] = (p.pins || []).map(asPin);
  const strike = p.then === 'strike' ? interpolate(f, [d * 0.55, d * 0.75], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) : 0;
  return (<Svg><WorldMap />
    <g clipPath="url(#mapclip)">
      {names.map((n, i) => { const s = useSpring(i * 8, first); const feat = SECTORS[n] ? sector(n) : shape(n);
        const c = p.color ? (C as any)[p.color] : col(n, i); const [x, y] = proj(PLACES[n] || geoCentroid(feat)) || [0, 0];
        return (<g key={n}>
          <path d={path(feat) || ''} fill={c} fillOpacity={0.85 * s} stroke={c} strokeWidth={3} />
          {SECTORS[n] ? <circle cx={x} cy={y} r={34 * s} fill="none" stroke={c} strokeWidth={5} /> : null}
          <Txt x={x + (p.labelDx || 0)} y={SECTORS[n] ? y - 52 : y + 12} t={(p.label || n).toUpperCase()} c={C.text} s={40} o={s} />
          {strike > 0 ? <line x1={x - 260} y1={y - 90} x2={x - 260 + 520 * strike} y2={y - 90 + 180 * strike}
            stroke="#FF5A5F" strokeWidth={16} strokeLinecap="round" /> : null}
        </g>); })}
    </g>
    {pins.map((pin, i) => { const s = useSpring(6 + i * 5, first); const [x, y] = proj(PLACES[pin.name]) || [0, 0];
      const home = pin.name === 'Paris' || pin.name === 'Mainland France';
      return (<g key={pin.name} opacity={s}>
        <circle cx={x} cy={y} r={(home ? 16 : 12) * s} fill={home ? C.accent : C.second} stroke={C.bg} strokeWidth={3} />
        <circle cx={x} cy={y} r={30 * s} fill="none" stroke={home ? C.accent : C.second} strokeWidth={2} opacity={0.5} />
        {pin.label ? <Txt x={x + (pin.dx || 0)} y={y + (pin.dy ?? -26)} t={pin.label} c={home ? C.accent : C.text} s={26} /> : null}
      </g>); })}
  </Svg>);
};

// A route drawn between two places along the great circle, with a moving marker.
export const CameraPan: React.FC<SceneP> = ({p, d, first}) => {
  const f = useCurrentFrame(); const proj = worldProj(); const path = pathFor(proj);
  const A = PLACES[p.from], B = PLACES[p.to]; const ip = geoInterpolate(A, B);
  const t = first ? 1 : interpolate(f, [6, d * 0.8], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const pts: [number, number][] = []; for (let i = 0; i <= 80; i++) pts.push(ip((i / 80) * t) as [number, number]);
  const [ax, ay] = proj(A) || [0, 0], [bx, by] = proj(B) || [0, 0], [mx, my] = proj(ip(t)) || [0, 0];
  const sb = interpolate(t, [0.92, 1], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (<Svg><WorldMap />
    <path d={path({type: 'LineString', coordinates: pts} as any) || ''} fill="none" stroke={C.accent} strokeWidth={6}
      strokeDasharray="18 12" strokeLinecap="round" />
    <circle cx={ax} cy={ay} r={14} fill={C.second} /><Txt x={ax} y={ay - 30} t={p.from.toUpperCase()} c={C.text} s={30} a="start" />
    <circle cx={bx} cy={by} r={14 * Math.max(sb, 0.01)} fill={C.second} />
    <Txt x={bx} y={by + 52} t={p.to.toUpperCase()} c={C.text} s={30} o={sb} />
    <circle cx={mx} cy={my} r={18} fill={C.accent} stroke={C.bg} strokeWidth={4} />
    {p.caption ? <Txt x={W / 2} y={MAP_BOTTOM + 90} t={p.caption} c={C.muted} s={38} o={sb} /> : null}
  </Svg>);
};

// Big numbers counting up, one row per item; the accent item is ours.
export const CountUp: React.FC<SceneP> = ({p, first}) => {
  const f = useCurrentFrame(); const items: [string, number][] = p.items || [];
  const rowH = items.length > 1 ? 330 : 0, y0 = 860 - (rowH * (items.length - 1)) / 2;
  return (<Svg>{items.map(([name, v], i) => {
    const s = useSpring(i * 10, first);
    const shown = first ? v : Math.round(interpolate(f, [4 + i * 10, 28 + i * 10], [0, v], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));
    const c = p.accent ? C.accent : i === 0 ? C.second : C.third; const y = y0 + i * rowH;
    return (<g key={name} opacity={s} transform={`translate(0 ${(1 - s) * 50})`}>
      <text x={W / 2} y={y} textAnchor="middle" fontFamily={fonts.display} fontWeight={700} fontSize={p.accent ? 360 : 260} fill={c}>{shown}</text>
      <text x={W / 2} y={y + (p.accent ? 110 : 90)} textAnchor="middle" fontFamily={fonts.display} fontWeight={700}
        fontSize={p.accent ? 84 : 64} fill={C.text} letterSpacing={4}>{name.toUpperCase()}</text>
      <text x={W / 2} y={y + (p.accent ? 170 : 140)} textAnchor="middle" fontFamily={fonts.body} fontWeight={700}
        fontSize={36} fill={C.muted}>{p.unit || 'time zones'}</text>
    </g>); })}</Svg>);
};

// Two analogue clocks whose hands sweep to the given times.
export const SplitClock: React.FC<SceneP> = ({p, first}) => {
  const f = useCurrentFrame();
  const clocks: [string, string][] = [p.left, p.right];
  return (<Svg>{clocks.map(([city, time], i) => {
    const s = useSpring(i * 10, first); const [hh, mm] = time.split(':').map(Number);
    const t = first ? 1 : interpolate(f, [8 + i * 10, 40 + i * 10], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
    const hourA = (((hh % 12) + mm / 60) * 30) * t + 360 * (1 - t), minA = mm * 6 * t + 720 * (1 - t);
    const cx = 280 + i * 520, cy = 860, r = 215, c = i === 0 ? C.accent : C.second;
    const hand = (ang: number, len: number) => [cx + len * Math.sin(rad(ang)), cy - len * Math.cos(rad(ang))];
    const [hx, hy] = hand(hourA, r * 0.55), [mx, my] = hand(minA, r * 0.82);
    const night = hh < 6 || hh >= 20;
    return (<g key={city} opacity={s}>
      <circle cx={cx} cy={cy} r={r} fill={night ? '#121A33' : '#1E2A4A'} stroke={c} strokeWidth={10} />
      {Array.from({length: 12}, (_, k) => { const [x1, y1] = hand(k * 30, r * 0.86), [x2, y2] = hand(k * 30, r * 0.96);
        return <line key={k} x1={x1} y1={y1} x2={x2} y2={y2} stroke={C.muted} strokeWidth={k % 3 === 0 ? 8 : 4} />; })}
      <line x1={cx} y1={cy} x2={hx} y2={hy} stroke={C.text} strokeWidth={14} strokeLinecap="round" />
      <line x1={cx} y1={cy} x2={mx} y2={my} stroke={C.text} strokeWidth={8} strokeLinecap="round" />
      <circle cx={cx} cy={cy} r={14} fill={c} />
      <Txt x={cx} y={cy + r + 90} t={city.toUpperCase()} c={C.text} s={58} />
      <Txt x={cx} y={cy + r + 170} t={time} c={c} s={84} />
      <Txt x={cx} y={cy + r + 225} t={night ? 'night' : 'daytime'} c={C.muted} s={34} />
    </g>); })}</Svg>);
};
