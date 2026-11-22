import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {C, fonts, useColor} from '../theme';
import {decimalsOf, fmtNum, Label, SceneP, Svg, useDims, useSpringAt} from './common';

export const NumberScene: React.FC<SceneP> = ({p, first}) => {
  const f = useCurrentFrame(); const {W, area, k, portrait} = useDims(); const col = useColor();
  const items: [string, number][] = p.items || [];
  const n = Math.max(items.length, 1); const cy0 = (area.y0 + area.y1) / 2 - ((n - 1) * 260 * k) / 2;
  return (<Svg>{items.map(([label, v], i) => {
    const s = useSpringAt(i * 8, first); const shown = first && i === 0 ? v : interpolate(f, [i * 8, i * 8 + 28], [0, v], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
    const cx = portrait || n === 1 ? W / 2 : area.x0 + ((area.x1 - area.x0) * (i + 0.5)) / n; const cy = portrait || n === 1 ? cy0 + i * 260 * k : (area.y0 + area.y1) / 2;
    const c = p.accent || i === 0 ? C.accent : col(label, i);
    return (<g key={label} opacity={s}>
      <text x={cx} y={cy + 40} textAnchor="middle" fontFamily={fonts.display} fontWeight={700} fontSize={(n > 1 ? 190 : 260) * k} fill={c}>
        {fmtNum(shown, decimalsOf(v))}{p.suffix || ''}</text>
      <Label x={cx} y={cy + 120 * k} text={label} size={46 * k} color={C.text} />
    </g>); })}
    {p.stamp ? (() => { const s = useSpringAt(26, false); return (
      <g transform={`translate(${W / 2 + 230 * k} ${area.y0 + 160 * k}) rotate(-12) scale(${0.6 + 0.4 * s})`} opacity={s}>
        <rect x={-150 * k} y={-60 * k} width={300 * k} height={110 * k} rx={18} fill="none" stroke={C.second} strokeWidth={8} />
        <text x={0} y={22 * k} textAnchor="middle" fontFamily={fonts.display} fontWeight={700} fontSize={70 * k} fill={C.second}>{p.stamp}</text></g>); })() : null}
  </Svg>);
};

export const BarsScene: React.FC<SceneP> = ({p, first}) => {
  const f = useCurrentFrame(); const {W, area, k} = useDims(); const col = useColor();
  const bars: [string, number][] = p.bars || []; const max = Math.max(...bars.map((b) => b[1]));
  const base = area.y1 - 120 * k, maxH = base - area.y0 - 140 * k;
  const bw = Math.min(300 * k, ((area.x1 - area.x0) * 0.7) / bars.length); const gap = (W - bars.length * bw) / (bars.length + 1);
  return (<Svg>{bars.map(([name, v], i) => {
    const s = useSpringAt(6 + i * 12, first); const h = Math.max(maxH * (v / max) * s, 10); const x = gap + i * (bw + gap);
    const shown = first ? v : interpolate(f, [6 + i * 12, 34 + i * 12], [0, v], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
    return (<g key={name}>
      <rect x={x} y={base - h} width={bw} height={h} rx={20 * k} fill={col(name, i)} />
      <text x={x + bw / 2} y={base - h - 28 * k} textAnchor="middle" fontFamily={fonts.display} fontWeight={700} fontSize={64 * k} fill={col(name, i)}>
        {fmtNum(shown, decimalsOf(v))}{p.unit ? <tspan fontSize={36 * k}>{` ${p.unit}`}</tspan> : null}</text>
      <Label x={x + bw / 2} y={base + 64 * k} text={name} size={46 * k} />
    </g>); })}</Svg>);
};

export const CardsScene: React.FC<SceneP> = ({p, first}) => {
  const f = useCurrentFrame(); const {W, area, k, portrait} = useDims(); const col = useColor();
  const cells: any[] = (p.cells || []).map((c: any) => (Array.isArray(c) ? c : [c, null]));
  const n = cells.length; const gap = 28 * k;
  const cols = portrait ? (n > 4 ? 2 : 1) : Math.min(n, 4); const rows = Math.ceil(n / cols);
  const cw = ((area.x1 - area.x0) - gap * (cols - 1)) / cols; const ch = Math.min(portrait ? 190 : 260, ((area.y1 - area.y0) - gap * (rows - 1)) / rows);
  const y0 = (area.y0 + area.y1) / 2 - (rows * ch + (rows - 1) * gap) / 2;
  return (<Svg>{cells.map(([title, sub], i) => {
    const s = useSpringAt(i * 9, first); const r = Math.floor(i / cols), c = i % cols;
    const x = area.x0 + c * (cw + gap), y = y0 + r * (ch + gap);
    const struck = p.cross_out_after !== undefined && i >= p.cross_out_after && f > 40 + i * 9;
    const accent = i === 0 ? C.accent : i === 1 ? C.second : C.third;
    return (<g key={i} opacity={s} transform={`translate(0 ${(1 - s) * 40})`}>
      <rect x={x} y={y} width={cw} height={ch} rx={26 * k} fill="rgba(255,255,255,0.06)" stroke={accent} strokeWidth={4} />
      <rect x={x} y={y} width={12 * k} height={ch} rx={6} fill={accent} />
      <text x={x + cw / 2} y={y + ch / 2 + (sub ? -6 : 22) * k} textAnchor="middle" fontFamily={fonts.display} fontWeight={700}
        fontSize={(String(title).length > 18 ? 48 : 60) * k} fill={C.text}>{title}</text>
      {sub ? <text x={x + cw / 2} y={y + ch / 2 + 56 * k} textAnchor="middle" fontFamily={fonts.body} fontWeight={700} fontSize={40 * k} fill={accent}>{sub}</text> : null}
      {struck ? <line x1={x + 30} y1={y + ch / 2} x2={x + cw - 30} y2={y + ch / 2} stroke="#FF5A5F" strokeWidth={10} strokeLinecap="round" /> : null}
    </g>); })}
    {p.stamp ? (() => { const s = useSpringAt(n * 9 + 10, false); return (
      <g opacity={s} transform={`translate(${W / 2} ${y0 + rows * (ch + gap) + 90 * k}) scale(${0.7 + 0.3 * s})`}>
        <text textAnchor="middle" fontFamily={fonts.display} fontWeight={700} fontSize={72 * k} fill={C.accent}>{p.stamp}</text></g>); })() : null}
  </Svg>);
};

export const KineticScene: React.FC<SceneP> = ({p, onScreen, first}) => {
  const {W, area, k} = useDims();
  const text: string = p.text || onScreen || '';
  const parts = text.includes(' · ') ? text.split(' · ') : text.split(' ');
  const size = Math.min(150, 1600 / Math.max(...parts.map((w) => w.length), 4)) * k * (parts.length > 4 ? 0.8 : 1);
  const cy = (area.y0 + area.y1) / 2;
  return (<Svg>{parts.map((w, i, arr) => { const s = useSpringAt(i * 4, first);
    return (<text key={i} x={W / 2} y={cy + (i - (arr.length - 1) / 2) * size * 1.08 + size / 3} textAnchor="middle" fontFamily={fonts.display}
      fontWeight={700} fontSize={size} fill={i === arr.length - 1 ? C.accent : C.text} opacity={s}
      transform={`translate(0 ${(1 - s) * 60})`}>{w}</text>); })}</Svg>);
};

export const TimelineScene: React.FC<SceneP> = ({p, first}) => {
  const {area, k} = useDims(); const events: [number | string, string][] = p.events || [];
  const y = (area.y0 + area.y1) / 2; const n = events.length; const x = (i: number) => area.x0 + 80 + ((area.x1 - area.x0 - 160) * (n === 1 ? 0.5 : i / (n - 1)));
  const line = useSpringAt(0, first);
  return (<Svg>
    <line x1={area.x0 + 40} y1={y} x2={area.x0 + 40 + (area.x1 - area.x0 - 80) * line} y2={y} stroke={C.landEdge} strokeWidth={6} strokeLinecap="round" />
    {events.map(([yr, label], i) => { const s = useSpringAt(8 + i * 12, first); const c = i === n - 1 ? C.accent : i === 0 ? C.second : C.third;
      return (<g key={i} opacity={s}>
        <circle cx={x(i)} cy={y} r={20 * k * (0.5 + 0.5 * s)} fill={c} stroke={C.bg} strokeWidth={5} />
        <Label x={x(i)} y={y - 50 * k} text={String(yr)} size={70 * k} color={c} />
        <Label x={x(i)} y={y + 80 * k} text={label} size={(label.length > 20 ? 30 : 38) * k} />
      </g>); })}
  </Svg>);
};

export const ClocksScene: React.FC<SceneP> = ({p, first}) => {
  const {W, area, k, portrait} = useDims(); const clocks: [string, string][] = [p.left, p.right].filter(Boolean);
  return (<Svg>{clocks.map(([city, time], i) => {
    const s = useSpringAt(i * 10, first); const [hh, mm] = time.split(':').map(Number);
    const cx = portrait ? W / 2 : area.x0 + ((area.x1 - area.x0) * (i + 0.5)) / 2; const cy = portrait ? area.y0 + 230 + i * 480 : (area.y0 + area.y1) / 2 - 40;
    const r = 170 * (portrait ? 1 : 0.9); const c = i === 0 ? C.second : C.accent;
    const ha = ((hh % 12) + mm / 60) * 30 * (Math.PI / 180), ma = mm * 6 * (Math.PI / 180);
    return (<g key={city} opacity={s}>
      <circle cx={cx} cy={cy} r={r} fill="rgba(255,255,255,0.05)" stroke={c} strokeWidth={8} />
      {Array.from({length: 12}, (_, j) => { const a = (j * 30 * Math.PI) / 180; return <line key={j} x1={cx + Math.sin(a) * r * 0.85} y1={cy - Math.cos(a) * r * 0.85} x2={cx + Math.sin(a) * r * 0.95} y2={cy - Math.cos(a) * r * 0.95} stroke={C.muted} strokeWidth={5} />; })}
      <line x1={cx} y1={cy} x2={cx + Math.sin(ha) * r * 0.5} y2={cy - Math.cos(ha) * r * 0.5} stroke={C.text} strokeWidth={12} strokeLinecap="round" />
      <line x1={cx} y1={cy} x2={cx + Math.sin(ma) * r * 0.78} y2={cy - Math.cos(ma) * r * 0.78} stroke={c} strokeWidth={8} strokeLinecap="round" />
      <Label x={cx} y={cy + r + 70 * k} text={`${city} ${time}`} size={54 * k} color={c} />
    </g>); })}</Svg>);
};
