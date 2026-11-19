import * as topojson from 'topojson-client';
import {geoAzimuthalEqualArea, geoCentroid, geoMercator, geoPath, GeoProjection} from 'd3-geo';
import world from 'world-atlas/countries-50m.json';

const topo: any = world;
const geoms: any[] = topo.objects.countries.geometries;

// ISO 3166-1 numeric codes of African countries (+ Somaliland, which has no code).
const AFRICA = new Set([12, 24, 204, 72, 854, 108, 120, 132, 140, 148, 174, 178, 180, 384, 262, 818, 226, 232, 748, 231,
  266, 270, 288, 324, 624, 404, 426, 430, 434, 450, 454, 466, 478, 480, 504, 508, 516, 562, 566, 646, 678, 686, 690, 694,
  706, 710, 728, 729, 834, 768, 788, 800, 894, 716, 732]);
const IDS: Record<string, number> = {
  Greenland: 304, USA: 840, China: 156, India: 356, Russia: 643, Australia: 36, 'Saudi Arabia': 682,
  'DR Congo': 180, Canada: 124, Brazil: 76, France: 250,
};

export const land: any = topojson.feature(topo, topo.objects.land);
const africa: any = topojson.merge(topo, geoms.filter((g) => AFRICA.has(Number(g.id)) || g.properties?.name === 'Somaliland'));

// The USA split into its contiguous states and Alaska, so packing scenes can
// place them separately (Hawaii, ~0.3% of the area, is left out of the drawing).
function usaPart(part: 'USA (48 states)' | 'Alaska'): any {
  const f: any = topojson.feature(topo, geoms.find((x) => Number(x.id) === 840));
  const polys = (f.geometry.type === 'MultiPolygon' ? f.geometry.coordinates : [f.geometry.coordinates]).filter((poly: any) => {
    const c = geoCentroid({type: 'Polygon', coordinates: poly} as any);
    return part === 'Alaska' ? c[1] > 50 : c[1] > 24 && c[1] <= 50 && c[0] > -130;
  });
  return {type: 'Feature', properties: {name: part}, geometry: {type: 'MultiPolygon', coordinates: polys}};
}

export function shape(name: string): any {
  if (name === 'Africa') return africa;
  if (name === 'USA (48 states)' || name === 'Alaska') return usaPart(name);
  const g = geoms.find((x) => Number(x.id) === IDS[name] || x.properties?.name === name);
  if (!g) throw new Error(`Unknown shape: ${name}`);
  return topojson.feature(topo, g);
}

const rad = (d: number) => (d * Math.PI) / 180;
const mercY = (lat: number) => Math.log(Math.tan(Math.PI / 4 + rad(lat) / 2));

// A Mercator view framed on a lon/lat box, used by every "real map" scene so the
// world never jumps between scenes.
export type View = {lon0: number; lon1: number; latTop: number; top: number; width: number};
export const ATLANTIC: View = {lon0: -76, lon1: 56, latTop: 84, top: 300, width: 1080};

export function mercatorFor(v: View, shiftLon = 0, rotate: [number, number] = [0, 0]): GeoProjection {
  const S = v.width / rad(v.lon1 - v.lon0);
  const centerLon = (v.lon0 + v.lon1) / 2;
  const Tx = v.width / 2 - S * rad(centerLon) + S * rad(shiftLon);
  const Ty = v.top + S * mercY(v.latTop);
  return geoMercator().scale(S).translate([Tx, Ty]).rotate([rotate[0], rotate[1], 0]).precision(0.2);
}

// True-size drawing: each shape in its own equal-area projection, same scale for all.
export function trueSize(feature: any, scale: number, cx: number, cy: number): string {
  const [lon, lat] = geoCentroid(feature);
  const p = geoAzimuthalEqualArea().rotate([-lon, -lat]).scale(scale).translate([cx, cy]).precision(0.2);
  return geoPath(p)(feature) || '';
}

export const pathFor = (p: GeoProjection) => geoPath(p);
export {geoCentroid};
