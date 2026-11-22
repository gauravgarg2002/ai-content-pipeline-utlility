import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {geoCircle, geoGraticule10} from 'd3-geo';
import {C, useColor} from '../theme';
import {ATLANTIC, BBox, Box, geoCentroid, land, lerpBox, makeProjection, pathFor, place, shape, WORLD} from '../geo';
import {Label, SceneP, Svg, useDims, useProgress} from './common';

const VIEWS: Record<string, BBox> = {
  world: WORLD, atlantic: ATLANTIC, usa: [-125, 23, -66, 50], alaska: [-180, 50, -128, 72],
  aleutians: [168, 49, 200, 58], usa_alaska: [-180, 18, -60, 72], asia: [55, -12, 150, 50],
  france_world: [-180, -55, 180, 70], canada: [-142, 41, -52, 84], arctic_canada: [-125, 60, -60, 84],
  europe_africa: [-30, -38, 60, 72], pacific_indian: [-160, -35, 60, 25],
};
const resolve = (v: any, fallback: BBox): BBox => {
  if (!v) return fallback;
  if (typeof v === 'string') return VIEWS[v] || fallback;
  if (Array.isArray(v) && v.length === 4 && typeof v[0] === 'number') return v as BBox;
  if (v.around) { const c = place(v.around) || [0, 0]; const dl = (v.km || 1500) / 111; return [c[0] - dl * 1.6, c[1] - dl, c[0] + dl * 1.6, c[1] + dl]; }
  return fallback;
};

const at = (d: number, frac: number | undefined, i: number, step = 0.08) => Math.round(d * (frac ?? Math.min(0.1 + i * step, 0.6)));
const appear = (f: number, start: number) => interpolate(f, [start, start + 12], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

export const GeoScene: React.FC<SceneP> = ({p, d, first}) => {
  const f = useCurrentFrame(); const {area, k} = useDims(); const col = useColor();
  const box: Box = [[area.x0, area.y0], [area.x1, area.y1]];
  const kind: string = p.projection || 'mercator';
  const vFrom = resolve(p.view?.from ?? p.view, kind === 'mercator' ? ATLANTIC : WORLD);
  const vTo = resolve(p.view?.to, vFrom);
  const t = useProgress(d, 0.05, 0.7);
  const bbox = lerpBox(vFrom, vTo, t);
  const spin = p.spin ? t * 60 : 0;
  const center: [number, number] | undefined = p.center ? [p.center[0] + spin, p.center[1]] : undefined;
  const g = (k0: number) => (first && k0 === 0 ? 1 : appear(f, k0));

  const render = (kindNow: string, opacity: number) => {
    const proj = makeProjection(kindNow, bbox, box, center); const path = pathFor(proj);
    const P = (c: [number, number]) => proj(c) || [-999, -999];
    const fills: any[] = [...(p.fills || []), ...(p.highlight || []), ...(p.shapes || [])].map((x: any) => (typeof x === 'string' ? {name: x} : x));
    return (
      <g opacity={opacity}>
        {kindNow !== 'mercator' ? <path d={path({type: 'Sphere'} as any) || ''} fill="rgba(60,80,140,0.12)" stroke={C.landEdge} strokeWidth={2} /> : null}
        {p.graticule !== false ? <path d={path(geoGraticule10()) || ''} fill="none" stroke={C.grid} strokeWidth={1.4} /> : null}
        <path d={path(land) || ''} fill={C.land} stroke={C.landEdge} strokeWidth={1.1} />
        {(p.heat || []).map((n: string, i: number) => { const s = shape(n); return s ? <path key={n} d={path(s) || ''} fill={C.third} fillOpacity={0.75 * appear(f, at(d, undefined, i, 0.03))} /> : null; })}
        {fills.map((x, i) => { const s = shape(x.name); if (!s) return null; const o = g(at(d, x.at ?? (i === 0 ? 0 : undefined), i));
          const c = x.color || col(x.name, i); const [lx, ly] = P(geoCentroid(s));
          return (<g key={x.name}><path d={path(s) || ''} fill={c} fillOpacity={0.85 * o} stroke={c} strokeWidth={2.5} strokeOpacity={o} />
            {x.label !== false && p.labels !== false ? <Label x={lx} y={ly} text={x.label || x.name} size={40 * k} o={o} /> : null}</g>); })}
        {p.tissot ? (p.tissot.lats || [0, 25, 45, 60, 70]).map((lat: number, li: number) => (p.tissot.lons || [-60, -30, 0, 30]).map((lon: number) => {
          const s = appear(f, at(d, undefined, li, 0.06));
          return <path key={`${lat},${lon}`} d={path(geoCircle().center([lon, lat]).radius((p.tissot.radius || 4) * Math.max(s, 0.01))()) || ''}
            fill="rgba(255,255,255,0.12)" stroke={C.text} strokeWidth={2.2} />; })) : null}
        {p.meridian !== undefined ? (() => { const s = appear(f, at(d, 0.15, 0)); const pts = Array.from({length: 33}, (_, i) => [p.meridian, -80 + i * 5]);
          return <path d={path({type: 'LineString', coordinates: pts} as any) || ''} fill="none" stroke={C.accent} strokeWidth={4} strokeDasharray="16 10" opacity={s} />; })() : null}
        {(p.circles || []).map((c: any, i: number) => { const s0 = at(d, c.at, i); const s = first && s0 === 0 ? 1 : interpolate(f, [s0, s0 + 25], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
          const r = ((c.radiusKm || 1000) / 6371) * (180 / Math.PI) * s;
          return <path key={i} d={path(geoCircle().center(c.center).radius(Math.max(r, 0.01)).precision(1)()) || ''} fill="rgba(255,181,71,0.05)" stroke={C.accent} strokeWidth={7} strokeDasharray="18 10" />; })}
        {(p.lines || []).map((ln: any, i: number) => { const s0 = at(d, ln.at, i); const s = interpolate(f, [s0, s0 + 30], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
          const coords = (ln.coords || ln.places.map((n: string) => place(n))) as [number, number][];
          const dpath = ln.straight ? `M${coords.map((c) => P(c).join(',')).join('L')}` : path({type: 'LineString', coordinates: coords} as any) || '';
          return <path key={i} d={dpath} pathLength={1} fill="none" stroke={ln.color || C.accent} strokeWidth={6} strokeDasharray={`${s} 1`} strokeLinecap="round" />; })}
        {p.measure ? (() => { const a = place(p.measure.a)!, b = place(p.measure.b)!; const s = appear(f, at(d, p.measure.at ?? 0.3, 0)); const [ax, ay] = P(a), [bx, by] = P(b);
          return (<g opacity={s}><line x1={ax} y1={ay} x2={bx} y2={by} stroke={C.accent} strokeWidth={5} strokeDasharray="12 8" />
            <Label x={(ax + bx) / 2} y={(ay + by) / 2 - 30} text={p.measure.label} color={C.accent} size={56 * k} /></g>); })() : null}
        {(p.pins || []).map((pn: any, i: number) => { const pos = pn.coords || place(pn.place || pn.name); if (!pos) return null; const s = g(at(d, pn.at, i, 0.05));
          const [x, y] = P(pos); const c = pn.color || C.accent;
          return (<g key={i} opacity={s}><circle cx={x} cy={y} r={11 * (0.6 + 0.4 * s)} fill={c} stroke={C.bg} strokeWidth={4} />
            {pn.label !== '' ? <Label x={x + (pn.dx || 0)} y={y + (pn.dy ?? -26)} text={pn.label || pn.place || pn.name} size={(pn.size || 34) * k} color={pn.labelColor || C.text} /> : null}</g>); })}
        {p.strike ? (() => { const s = shape(p.strike); if (!s) return null; const [[x0, y0], [x1, y1]] = path.bounds(s); const st = appear(f, at(d, p.strikeAt ?? 0.45, 0));
          return <g opacity={st}><line x1={x0} y1={y0} x2={x1} y2={y1} stroke="#FF5A5F" strokeWidth={12} strokeLinecap="round" /><line x1={x1} y1={y0} x2={x0} y2={y1} stroke="#FF5A5F" strokeWidth={12} strokeLinecap="round" /></g>; })() : null}
      </g>
    );
  };

  if (p.morph) {
    const m = interpolate(f, [d * 0.3, d * 0.65], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
    return <Svg>{render(p.morph.from, 1 - m)}{render(p.morph.to, m)}</Svg>;
  }
  return <Svg>{render(kind, 1)}</Svg>;
};
