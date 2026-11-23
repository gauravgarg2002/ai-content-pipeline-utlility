import * as topojson from 'topojson-client';
import {
  geoAzimuthalEqualArea, geoCentroid, geoEqualEarth, geoMercator, geoOrthographic, geoPath, geoProjection, GeoProjection,
} from 'd3-geo';
import world from 'world-atlas/countries-50m.json';

const topo: any = world;
const geoms: any[] = topo.objects.countries.geometries;
const rad = (d: number) => (d * Math.PI) / 180;

// ISO 3166-1 numeric codes of African countries (+ Somaliland, which has no code).
const AFRICA = new Set([12, 24, 204, 72, 854, 108, 120, 132, 140, 148, 174, 178, 180, 384, 262, 818, 226, 232, 748, 231,
  266, 270, 288, 324, 624, 404, 426, 430, 434, 450, 454, 466, 478, 480, 504, 508, 516, 562, 566, 646, 678, 686, 690, 694,
  706, 710, 728, 729, 834, 768, 788, 800, 894, 716, 732]);
const EUROPE = new Set([8, 20, 40, 56, 70, 100, 112, 191, 196, 203, 208, 233, 246, 250, 276, 300, 348, 352, 372, 380, 428,
  438, 440, 442, 470, 492, 498, 499, 528, 807, 578, 616, 620, 642, 674, 688, 703, 705, 724, 752, 756, 804, 826]);
const NORTH_AMERICA = new Set([124, 840, 484]);
const SOUTH_AMERICA = new Set([32, 68, 76, 152, 170, 218, 238, 254, 328, 600, 604, 740, 858, 862]);
const IDS: Record<string, number> = {
  Greenland: 304, USA: 840, China: 156, India: 356, Russia: 643, RUS: 643, Australia: 36, 'Saudi Arabia': 682,
  'DR Congo': 180, Canada: 124, Brazil: 76, France: 250, Japan: 392, JPN: 392, GBR: 826, 'United Kingdom': 826, IND: 356,
  Bangladesh: 50, Pakistan: 586, Indonesia: 360, Vietnam: 704, Philippines: 608, Myanmar: 104, Thailand: 764, Nepal: 524,
  'North Korea': 408, 'South Korea': 410, Spain: 724, Poland: 616, Kazakhstan: 398, Mongolia: 496, Chile: 152, Ecuador: 218,
  Argentina: 32, Bolivia: 68, Colombia: 170, Guyana: 328, Paraguay: 600, Peru: 604, Suriname: 740, Uruguay: 858, Venezuela: 862,
  'Sri Lanka': 144,
};
const GROUPS: Record<string, Set<number>> = {Africa: AFRICA, Europe: EUROPE, 'North America': NORTH_AMERICA, 'South America': SOUTH_AMERICA};

// [lon, lat]
export const PLACES: Record<string, [number, number]> = {
  Paris: [2.35, 48.86], Tahiti: [-149.57, -17.54], 'French Polynesia': [-149.4, -17.6], Reunion: [55.53, -21.11],
  Guadeloupe: [-61.55, 16.25], Martinique: [-61.02, 14.64], 'French Guiana': [-53.13, 3.93],
  'Saint Pierre and Miquelon': [-56.27, 46.88], Mayotte: [45.17, -12.83], Kerguelen: [69.35, -49.28],
  'New Caledonia': [165.6, -21.3], 'Wallis and Futuna': [-176.2, -13.77], Marquesas: [-140.0, -9.0], 'Adelie Land': [139.0, -67.0],
  Delhi: [77.21, 28.61], Mumbai: [72.88, 19.08], Beijing: [116.4, 39.9], Manila: [120.98, 14.6], Jakarta: [106.85, -6.2],
  Tokyo: [139.69, 35.68], Maine: [-69.0, 45.3], 'Aleutian Islands': [-175, 52], Semisopochnoi: [179.77, 51.96],
  Amatignak: [-179.15, 51.27], Lisbon: [-9.14, 38.72], Salvador: [-38.5, -12.97], Milan: [9.19, 45.46],
  Montreal: [-73.57, 45.5], Oslo: [10.75, 59.91], Anchorage: [-149.9, 61.22],
  // week 2
  Reno: [-119.81, 39.53], 'Los Angeles': [-118.24, 34.05], 'San Diego': [-117.16, 32.72], 'San Francisco': [-122.42, 37.77],
  Perth: [115.86, -31.95], Brisbane: [153.03, -27.47], London: [-0.13, 51.51], Moscow: [37.62, 55.76], Kashgar: [75.99, 39.47],
  Mirzapur: [82.57, 25.15], Guwahati: [91.74, 26.14], Kathmandu: [85.32, 27.71], Madrid: [-3.7, 40.42], Warsaw: [21.01, 52.23],
  Tarawa: [173.0, 1.45], Kiritimati: [-157.4, 1.87], Pyongyang: [125.75, 39.03], Seoul: [126.98, 37.57],
  Ayodhya: [82.2, 26.8], Shringverpur: [81.64, 25.58], Prayagraj: [81.85, 25.44], Chitrakoot: [80.87, 25.2],
  Dandakaranya: [82.03, 19.08], Panchavati: [73.79, 20.01], Lepakshi: [77.6, 13.81], Kishkindha: [76.46, 15.33],
  Rameswaram: [79.31, 9.29], Dhanushkodi: [79.42, 9.15], Talaimannar: [79.73, 9.08], 'Sri Lanka': [80.7, 7.6],
};

export const land: any = topojson.feature(topo, topo.objects.land);
const cache: Record<string, any> = {};

function usaPart(part: string): any {
  const f: any = topojson.feature(topo, geoms.find((x) => Number(x.id) === 840));
  const polys = f.geometry.coordinates.filter((poly: any) => {
    const c = geoCentroid({type: 'Polygon', coordinates: poly} as any);
    return part === 'Alaska' ? c[1] > 50 : c[1] > 24 && c[1] <= 50 && c[0] > -130;
  });
  return {type: 'Feature', properties: {name: part}, geometry: {type: 'MultiPolygon', coordinates: polys}};
}

export function shape(name: string): any {
  if (cache[name]) return cache[name];
  let f: any;
  if (GROUPS[name]) {
    const set = GROUPS[name];
    f = topojson.merge(topo, geoms.filter((g) => set.has(Number(g.id)) || (name === 'Africa' && g.properties?.name === 'Somaliland')));
  } else if (name === 'USA (48 states)' || name === 'Alaska' || name === 'AK') {
    f = usaPart(name === 'AK' ? 'Alaska' : name);
  } else {
    const g = geoms.find((x) => Number(x.id) === IDS[name] || x.properties?.name === name);
    if (!g) return null;
    f = topojson.feature(topo, g);
  }
  cache[name] = f;
  return f;
}

export const place = (name: string): [number, number] | null => PLACES[name] || (shape(name) ? geoCentroid(shape(name)) : null);

// ---- projections ------------------------------------------------------------
const GP = Math.cos(rad(45));
const gallPetersRaw: any = (l: number, p: number) => [l * GP, Math.sin(p) / GP];
gallPetersRaw.invert = (x: number, y: number) => [x / GP, Math.asin(Math.max(-1, Math.min(1, y * GP)))];

export type Box = [[number, number], [number, number]];
export type BBox = [number, number, number, number]; // lonW, latS, lonE, latN (lonE may exceed 180)

function bboxPoints(b: BBox): any {
  const pts: [number, number][] = [];
  for (let i = 0; i <= 6; i++) for (let j = 0; j <= 6; j++) pts.push([b[0] + ((b[2] - b[0]) * i) / 6, b[1] + ((b[3] - b[1]) * j) / 6]);
  return {type: 'MultiPoint', coordinates: pts};
}

export function makeProjection(kind: string, b: BBox, box: Box, center?: [number, number]): GeoProjection {
  const cLon = (b[0] + b[2]) / 2;
  if (kind === 'ortho') {
    const [lon, lat] = center || [cLon, (b[1] + b[3]) / 2];
    return geoOrthographic().rotate([-lon, -lat]).fitExtent(box, {type: 'Sphere'} as any).precision(0.3);
  }
  if (kind === 'equal_area_local') {
    const [lon, lat] = center || [cLon, (b[1] + b[3]) / 2];
    return geoAzimuthalEqualArea().rotate([-lon, -lat]).fitExtent(box, bboxPoints(b)).precision(0.3);
  }
  const base: GeoProjection = kind === 'equal_earth' ? geoEqualEarth() : kind === 'gall_peters' ? geoProjection(gallPetersRaw) : geoMercator();
  const rotated = base.rotate([-cLon, 0]);
  const pts = bboxPoints(b);
  return rotated.fitExtent(box, pts).precision(0.3);
}

export const WORLD: BBox = [-180, -60, 180, 82];
export const ATLANTIC: BBox = [-76, -38, 56, 84];

export function lerpBox(a: BBox, b: BBox, t: number): BBox {
  return [0, 1, 2, 3].map((i) => a[i] + (b[i] - a[i]) * t) as BBox;
}

// True-size drawing: each shape in its own equal-area projection, same scale for all.
export function trueSize(feature: any, scale: number, cx: number, cy: number): string {
  const [lon, lat] = geoCentroid(feature);
  const p = geoAzimuthalEqualArea().rotate([-lon, -lat]).scale(scale).translate([cx, cy]).precision(0.2);
  return geoPath(p)(feature) || '';
}

export const pathFor = (p: GeoProjection) => geoPath(p);
export {geoCentroid};
