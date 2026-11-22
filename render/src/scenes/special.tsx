import React from 'react';
import {interpolate, useCurrentFrame, Easing} from 'remotion';
import {geoMercator} from 'd3-geo';
import {C, fonts, useColor} from '../theme';
import {ATLANTIC, Box, geoCentroid, land, makeProjection, pathFor, shape, trueSize} from '../geo';
import {fmtNum, Label, SceneP, Svg, useDims, useProgress, useSpringAt} from './common';

const rad = (d: number) => (d * Math.PI) / 180;

export const TrueSizeStack: React.FC<SceneP> = ({p, first}) => {
  const {W, area, k, portrait} = useDims(); const col = useColor(); const names: string[] = p.shapes || [];
  const n = Math.max(names.length, 1); const scale = (p.scale || 560) * (portrait ? 1 : 0.62);
  return (<Svg>{names.map((nm, i) => { const s = useSpringAt(i * 10, first);
    const cx = portrait ? W / 2 : area.x0 + ((area.x1 - area.x0) * (i + 0.5)) / n; const cy = portrait ? area.y0 + ((area.y1 - area.y0) * (i + 0.5)) / n : (area.y0 + area.y1) / 2 + 30;
    return (<g key={nm} opacity={s}><path d={trueSize(shape(nm), scale, cx, cy)} fill={col(nm, i)} fillOpacity={0.85} stroke={col(nm, i)} strokeWidth={3} />
      <Label x={cx} y={portrait ? cy - (area.y1 - area.y0) / n / 2 + 40 : area.y0 + 30} text={nm} size={44 * k} /></g>); })}</Svg>);
};

const PACK: Record<string, [number, number]> = {'USA (48 states)': [-110, -210], Alaska: [-310, -40], China: [20, 60], India: [60, 330]};
export const ShapePack: React.FC<SceneP> = ({p, first}) => {
  const {W, H, k, portrait} = useDims(); const z = portrait ? 1 : 0.56;
  const scale = 640 * z, cx = W / 2, cy = portrait ? 900 : H / 2 + 40;
  const pieces: string[] = (p.pieces || []).flatMap((n: string) => (n === 'USA' ? ['USA (48 states)', 'Alaska'] : [n]));
  const rem = useSpringAt(10 + pieces.length * 14 + 10, false);
  return (<Svg>
    <path d={trueSize(shape(p.container), scale, cx, cy)} fill="rgba(61,214,198,0.10)" stroke={C.second} strokeWidth={5} strokeDasharray="14 10" />
    <Label x={cx + 330 * z} y={cy + 330 * z} text={p.container} color={C.second} size={44 * k} />
    {pieces.map((n, i) => { const s = useSpringAt(10 + i * 14, first); const [dx, dy] = PACK[n] || [0, (i - 1) * 260];
      return (<g key={n} opacity={s} transform={`translate(0 ${(1 - s) * 500 * z})`}>
        <path d={trueSize(shape(n), scale, cx + dx * z, cy + dy * z)} fill={C.third} fillOpacity={0.85} stroke={C.bg} strokeWidth={3} />
        <Label x={cx + dx * z} y={cy + dy * z + 14} text={n === 'USA (48 states)' ? 'USA' : n} size={(n === 'Alaska' ? 30 : 40) * k} /></g>); })}
    {p.show_remainder ? <Label x={cx - 300 * z} y={cy + 420 * z} text="+7.6M km² left" color={C.second} size={50 * k} o={rem} upper={false} /> : null}
  </Svg>);
};

export const DragShape: React.FC<SceneP> = ({p, d}) => {
  const f = useCurrentFrame(); const {area, k} = useDims(); const col = useColor();
  const box: Box = [[area.x0, area.y0], [area.x1, area.y1]];
  const base = makeProjection('mercator', ATLANTIC, box); const [Tx, Ty] = base.translate(); const S = base.scale(); const cLon = -base.rotate()[0];
  const target = shape(p.land_on || 'Africa'); const mover = shape(p.shape || 'Greenland');
  const [lonG, latG] = geoCentroid(mover); const [lonT] = geoCentroid(target);
  const t = interpolate(f, [8, d * 0.8], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const latNow = latG + ((p.to_lat ?? 0) - latG) * t; const lonNow = lonG + (lonT - lonG) * t;
  const moving = geoMercator().scale(S).translate([Tx + S * rad(lonNow - cLon), Ty]).rotate([-lonG, latNow - latG]).precision(0.2);
  const [lx, ly] = moving([lonG, latG]) || [0, 0];
  const path = pathFor(base);
  return (<Svg>
    <path d={path(land) || ''} fill={C.land} stroke={C.landEdge} strokeWidth={1.1} />
    <path d={path(target) || ''} fill={col(p.land_on || 'Africa', 1)} fillOpacity={0.35} stroke={col(p.land_on || 'Africa', 1)} strokeWidth={3} />
    <path d={pathFor(moving)(mover) || ''} fill={col(p.shape || 'Greenland', 0)} fillOpacity={0.9} stroke={C.bg} strokeWidth={2} />
    <Label x={lx} y={ly + 16} text={p.shape || 'Greenland'} size={40 * k} />
  </Svg>);
};

// Coastline paradox: the same coast traced with a long ruler, then shorter ones.
export const RulerScene: React.FC<SceneP> = ({p, d, first}) => {
  const f = useCurrentFrame(); const {area, k, W} = useDims();
  const box: Box = [[area.x0, area.y0 + 120], [area.x1, area.y1]];
  const proj = makeProjection('mercator', [-142, 41, -52, 84], box); const path = pathFor(proj);
  const canada = shape('Canada'); const strides = p.strides || [400, 60, 10, 1];
  const phase = Math.min(strides.length - 1, Math.floor(useProgress(d, 0, 0.85) * strides.length * 0.999));
  const stride = strides[phase];
  const rings: number[][][] = (canada.geometry.type === 'MultiPolygon' ? canada.geometry.coordinates.flat() : canada.geometry.coordinates)
    .filter((r: number[][]) => r.length > (stride > 50 ? 60 : 6));
  const dStr = rings.map((r) => { const pts = r.filter((_, i) => i % stride === 0).map((c) => proj(c as any)).filter(Boolean) as number[][];
    return pts.length > 2 ? `M${pts.map((q) => q.join(',')).join('L')}Z` : ''; }).join('');
  const v0 = p.from_value || 202080, v1 = p.label_end || 265523;
  const val = first ? v0 : interpolate(f, [d * 0.15, d * 0.85], [v0, v1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (<Svg>
    <path d={path(land) || ''} fill={C.land} stroke="none" />
    <path d={dStr} fill="none" stroke={C.accent} strokeWidth={phase < 2 ? 5 : 2.5} strokeLinejoin="round" />
    {p.counter !== false ? <text x={W / 2} y={area.y0 + 80} textAnchor="middle" fontFamily={fonts.display} fontWeight={700} fontSize={110 * k} fill={C.accent}>{fmtNum(val)} km</text> : null}
    <Label x={W / 2} y={area.y1 - 20} text={`ruler: ${['very long', 'long', 'short', 'tiny'][phase] || 'tiny'}`} size={40 * k} color={C.muted} />
  </Svg>);
};

// ---- Family tree (epics) -----------------------------------------------------
const POS: Record<string, [number, number]> = {
  Ganga: [300, 120], Shantanu: [640, 120], Satyavati: [980, 120], Parashara: [1320, 120],
  Bhishma: [300, 300], Chitrangada: [560, 300], Vichitravirya: [820, 300], Ambika: [1060, 300], Ambalika: [1290, 300], Vyasa: [1520, 300], Maid: [1760, 300],
  Gandhari: [200, 490], Dhritarashtra: [440, 490], Vidura: [680, 490], Pandu: [960, 490], Kunti: [1200, 490], Madri: [1440, 490], Vasudeva: [1700, 490],
  Duryodhana: [180, 690], Duhshala: [360, 690], Yuyutsu: [560, 690], Karna: [790, 690], Yudhishthira: [990, 690], Bhima: [1150, 690],
  Arjuna: [1310, 690], Nakula: [1470, 690], Sahadeva: [1630, 690], Krishna: [1820, 690],
  Adhiratha: [690, 880], Radha: [890, 880], Draupadi: [1310, 880],
};
const MARRIAGES: [string, string][] = [['Ganga', 'Shantanu'], ['Shantanu', 'Satyavati'], ['Satyavati', 'Parashara'], ['Vichitravirya', 'Ambika'],
  ['Ambika', 'Ambalika'], ['Gandhari', 'Dhritarashtra'], ['Pandu', 'Kunti'], ['Kunti', 'Madri'], ['Adhiratha', 'Radha']];
const CHILDREN: [string, string[], string?][] = [
  ['Bhishma', ['Ganga', 'Shantanu']], ['Chitrangada', ['Shantanu', 'Satyavati']], ['Vichitravirya', ['Shantanu', 'Satyavati']], ['Vyasa', ['Satyavati', 'Parashara']],
  ['Dhritarashtra', ['Vyasa', 'Ambika'], 'niyoga'], ['Pandu', ['Vyasa', 'Ambalika'], 'niyoga'], ['Vidura', ['Vyasa', 'Maid'], 'niyoga'],
  ['Duryodhana', ['Gandhari', 'Dhritarashtra']], ['Duhshala', ['Gandhari', 'Dhritarashtra']], ['Yuyutsu', ['Dhritarashtra']],
  ['Yudhishthira', ['Pandu', 'Kunti']], ['Bhima', ['Pandu', 'Kunti']], ['Arjuna', ['Pandu', 'Kunti']], ['Nakula', ['Kunti', 'Madri']], ['Sahadeva', ['Kunti', 'Madri']],
  ['Karna', ['Kunti'], 'secret'], ['Krishna', ['Vasudeva']], ['Karna', ['Adhiratha', 'Radha'], 'foster'],
];
const EXTRA: [string, string, string][] = [['Kunti', 'Vasudeva', 'siblings'], ['Draupadi', 'Arjuna', 'marriage']];

export const TreeScene: React.FC<SceneP> = ({p}) => {
  const vis: string[] = p.nodes || []; const isVis = (n: string) => vis.includes(n);
  const nw = (n: string) => (POS[n][1] >= 690 && POS[n][1] < 880 ? 150 : 200);
  const mid = (ps: string[]) => { const xs = ps.map((q) => POS[q][0]); return [(Math.min(...xs) + Math.max(...xs)) / 2, POS[ps[0]][1]]; };
  const fresh = (n: string) => (p.new || []).includes(n);
  const hl = (n: string) => (p.highlight || []).includes(n);
  const dead = (n: string) => (p.deceased || []).includes(n);
  const label = (n: string) => (p.labels || {})[n] || n;
  const sub = (n: string) => (p.subs || {})[n];
  const sp = useSpringAt(6, false);
  const nodeO = (n: string) => (fresh(n) ? sp : 1);
  const dim = (p.highlight || []).length > 0;
  return (<Svg>
    {MARRIAGES.filter(([a, b]) => isVis(a) && isVis(b)).map(([a, b]) => (
      <line key={a + b} x1={POS[a][0]} y1={POS[a][1]} x2={POS[b][0]} y2={POS[b][1]} stroke={C.landEdge} strokeWidth={4} opacity={Math.min(nodeO(a), nodeO(b))} />))}
    {EXTRA.filter(([a, b]) => isVis(a) && isVis(b)).map(([a, b, kind]) => (
      <path key={a + b} d={`M${POS[a][0]},${POS[a][1] + 34} C${POS[a][0]},${POS[a][1] + 120} ${POS[b][0]},${POS[b][1] + 120} ${POS[b][0]},${POS[b][1] + 34}`}
        fill="none" stroke={kind === 'marriage' ? C.accent : C.muted} strokeWidth={4} strokeDasharray="4 10" strokeLinecap="round" opacity={Math.min(nodeO(a), nodeO(b))} />))}
    {CHILDREN.filter(([c, ps]) => isVis(c) && ps.every(isVis)).map(([c, ps, kind]) => { const [mx, my] = mid(ps); const [cx, cy] = POS[c];
      const y1 = my + (ps.length > 1 ? 0 : 34), ym = (my + cy) / 2 + 10;
      return <path key={c + ps.join()} d={`M${mx},${y1} L${mx},${ym} L${cx},${ym} L${cx},${cy - 34}`} fill="none"
        stroke={kind === 'secret' ? C.accent : kind === 'foster' ? C.muted : '#5A6A99'} strokeWidth={4}
        strokeDasharray={kind === 'secret' || kind === 'foster' ? '10 8' : undefined} opacity={nodeO(c)} />; })}
    {(p.groups || []).map((g: any) => { const ids = g.ids.filter(isVis); if (!ids.length) return null; const xs = ids.map((n: string) => POS[n][0]); const y = POS[ids[0]][1];
      return (<g key={g.label}><rect x={Math.min(...xs) - 95} y={y - 60} width={Math.max(...xs) - Math.min(...xs) + 190} height={150} rx={26} fill="none" stroke={g.color || C.second} strokeWidth={3} strokeDasharray="8 8" />
        <text x={(Math.min(...xs) + Math.max(...xs)) / 2} y={y + 115} textAnchor="middle" fontFamily={fonts.display} fontWeight={700} fontSize={30} fill={g.color || C.second}>{g.label.toUpperCase()}</text></g>); })}
    {vis.filter((n) => POS[n]).map((n) => { const [x, y] = POS[n]; const w = nw(n); const o = nodeO(n) * (dim && !hl(n) && !fresh(n) ? 0.45 : 1) * (dead(n) ? 0.6 : 1);
      const stroke = hl(n) ? C.accent : fresh(n) ? C.second : '#3A4870';
      return (<g key={n} opacity={o} transform={`translate(${x} ${y}) scale(${fresh(n) ? 0.8 + 0.2 * sp : 1})`}>
        <rect x={-w / 2} y={-34} width={w} height={68} rx={18} fill={hl(n) ? '#3A3220' : '#16203B'} stroke={stroke} strokeWidth={hl(n) || fresh(n) ? 5 : 3} />
        <text x={0} y={10} textAnchor="middle" fontFamily={fonts.display} fontWeight={700} fontSize={w < 200 ? 24 : 28} fill={C.text}>{label(n)}</text>
        {sub(n) ? <text x={0} y={62} textAnchor="middle" fontFamily={fonts.body} fontWeight={700} fontSize={20} fill={C.muted}>{sub(n)}</text> : null}
        {dead(n) ? <line x1={-w / 2 + 10} y1={0} x2={w / 2 - 10} y2={0} stroke={C.muted} strokeWidth={3} /> : null}
      </g>); })}
  </Svg>);
};
