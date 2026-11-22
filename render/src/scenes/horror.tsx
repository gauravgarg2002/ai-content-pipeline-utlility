import React from 'react';
import {interpolate, random, useCurrentFrame} from 'remotion';
import {SceneP} from './common';

// Atmosphere scenes for the Hindi horror channel. All shapes, no images.
// Palette: cold night blues, one warm window. 1920x1080.
const H = {sky0: '#05070D', sky1: '#0E1424', wall: '#141A26', wallEdge: '#1D2433', win: '#0A0D14', warm: '#F2B35A', warmDeep: '#7A4A12', fig: '#050505'};
const W0 = 1920, H0 = 1080;

const Grain: React.FC = () => {
  const f = useCurrentFrame();
  const dots = Array.from({length: 160}, (_, i) => [random(`x${i}${f % 6}`) * W0, random(`y${i}${f % 6}`) * H0, random(`r${i}`) * 1.6 + 0.4]);
  return <g opacity={0.35}>{dots.map(([x, y, r], i) => <circle key={i} cx={x} cy={y} r={r} fill="#9AA3B8" />)}</g>;
};
const Vignette: React.FC<{strength?: number}> = ({strength = 0.85}) => (
  <><defs><radialGradient id="vig" cx="50%" cy="50%" r="70%"><stop offset="55%" stopColor="#000" stopOpacity={0} /><stop offset="100%" stopColor="#000" stopOpacity={strength} /></radialGradient></defs>
    <rect width={W0} height={H0} fill="url(#vig)" /></>
);
const Rain: React.FC<{o?: number}> = ({o = 0.25}) => {
  const f = useCurrentFrame();
  return <g opacity={o} stroke="#8FA3C8" strokeWidth={1.6}>{Array.from({length: 90}, (_, i) => {
    const x = (random(`rx${i}`) * (W0 + 300) + f * 6) % (W0 + 300) - 150; const y = (random(`ry${i}`) * H0 + f * 34) % (H0 + 200) - 100;
    return <line key={i} x1={x} y1={y} x2={x - 10} y2={y + 46} />; })}</g>;
};
const flicker = (f: number, seed: string) => 0.9 + 0.1 * Math.sin(f / 5) * (random(`${seed}${Math.floor(f / 7)}`) > 0.85 ? 2.2 : 1);

// Figure behind glass. pose: comb | wave | point | stand | none
const Figure: React.FC<{x: number; y: number; s: number; pose: string; facing?: 'back' | 'side'}> = ({x, y, s, pose, facing = 'back'}) => {
  const f = useCurrentFrame(); const t = f / 30;
  const comb = Math.sin(t * 2.2) * 0.5 + 0.5;
  return (<g transform={`translate(${x} ${y}) scale(${s})`} fill={H.fig}>
    <path d="M-70,160 C-70,60 -50,10 0,10 C50,10 70,60 70,160 Z" />
    <path d="M-34,-40 C-50,20 -48,90 -40,140 L40,140 C48,90 50,20 34,-40 Z" opacity={0.95} />
    <circle cx={facing === 'side' ? 8 : 0} cy={-52} r={30} />
    {pose === 'comb' ? <path d={`M30,0 Q${55},${-40 - comb * 40} ${24},${-70 - comb * 30}`} stroke={H.fig} strokeWidth={14} fill="none" strokeLinecap="round" /> : null}
    {pose === 'wave' ? <path d={`M34,10 Q70,-30 ${60 + Math.sin(t * 3) * 18},${-90}`} stroke={H.fig} strokeWidth={14} fill="none" strokeLinecap="round" /> : null}
    {pose === 'point' ? <path d="M34,10 L120,-20 L170,-26" stroke={H.fig} strokeWidth={14} fill="none" strokeLinecap="round" /> : null}
    {pose === 'shh' ? <path d="M10,20 Q-10,-20 0,-44" stroke={H.fig} strokeWidth={10} fill="none" strokeLinecap="round" /> : null}
  </g>);
};

const Window: React.FC<{x: number; y: number; w: number; h: number; state: string; pose?: string; dust?: number; children?: React.ReactNode}> = ({x, y, w, h, state, pose = 'comb', dust = 0.25, children}) => {
  const f = useCurrentFrame(); const lit = state !== 'off'; const fl = flicker(f, `w${x}`);
  return (<g>
    <defs><radialGradient id={`glow${x}`} cx="50%" cy="55%" r="65%"><stop offset="0%" stopColor={H.warm} stopOpacity={0.95 * fl} /><stop offset="100%" stopColor={H.warmDeep} stopOpacity={0.9} /></radialGradient>
      <clipPath id={`clip${x}`}><rect x={x} y={y} width={w} height={h} /></clipPath></defs>
    {lit ? <rect x={x - 80} y={y - 80} width={w + 160} height={h + 160} fill={H.warm} opacity={0.08 * fl} rx={60} /> : null}
    <rect x={x} y={y} width={w} height={h} fill={lit ? `url(#glow${x})` : H.win} />
    <g clipPath={`url(#clip${x})`}>
      {lit && pose !== 'none' && state !== 'mirror' ? <Figure x={x + w * 0.5} y={y + h * 0.62} s={h / 420} pose={pose} /> : null}
      {children}
    </g>
    <rect x={x} y={y} width={w} height={h} fill="#C9CCD3" opacity={dust} />
    <rect x={x - 14} y={y - 14} width={w + 28} height={h + 28} fill="none" stroke="#1E2433" strokeWidth={28} />
    <line x1={x + w / 2} y1={y} x2={x + w / 2} y2={y + h} stroke="#1E2433" strokeWidth={14} />
  </g>);
};

const Lane: React.FC<{state: string; pose: string}> = ({state, pose}) => {
  const f = useCurrentFrame();
  const off = state === 'dark_end' ? interpolate(f, [60, 64], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) : 1;
  return (<>
    <defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={H.sky0} /><stop offset="100%" stopColor={H.sky1} /></linearGradient></defs>
    <rect width={W0} height={H0} fill="url(#sky)" />
    <circle cx={1600} cy={120} r={60} fill="#C8D2E8" opacity={0.18} />
    <rect x={260} y={0} width={1400} height={H0} fill={H.wall} />
    {[0, 1, 2].map((r) => [0, 1, 2, 3].map((c) => (r === 1 && c === 2) ? null :
      <rect key={`${r}${c}`} x={360 + c * 330} y={90 + r * 330} width={190} height={240} fill={H.win} stroke={H.wallEdge} strokeWidth={14} />))}
    <g opacity={off}><Window x={1020} y={420} w={190} h={240} state={state === 'off' || state === 'dark_end' && off < 0.5 ? 'off' : 'on'} pose={pose} /></g>
    <rect x={0} y={0} width={260} height={H0} fill="#07090F" />
    <rect x={1660} y={0} width={260} height={H0} fill="#07090F" />
    <Rain />
  </>);
};

const Room: React.FC<{v: string}> = ({v}) => {
  const f = useCurrentFrame();
  return (<>
    <rect width={W0} height={H0} fill="#0C111C" />
    <rect x={0} y={760} width={W0} height={320} fill="#080B12" />
    {/* window to the lane, opposite window visible */}
    <rect x={1220} y={170} width={480} height={460} fill="#0A0E17" stroke="#1E2433" strokeWidth={26} />
    <rect x={1290} y={260} width={150} height={190} fill={v === 'fog' ? '#2A3140' : '#101624'} />
    {v === 'fog' ? <rect x={1220} y={170} width={480} height={460} fill="#AEB6C6" opacity={0.28} /> : null}
    {/* bed */}
    <rect x={180} y={600} width={760} height={190} rx={20} fill="#151C2B" />
    <rect x={200} y={560} width={220} height={80} rx={30} fill="#1D2638" />
    {v === 'hair' ? <path d="M230,590 C300,610 330,575 400,600 C450,615 480,600 520,620" stroke="#020202" strokeWidth={4} fill="none" /> : null}
    {/* chair */}
    <g transform={v === 'chair' ? 'translate(1080 600) rotate(-18)' : 'translate(1000 600)'}>
      <rect x={0} y={0} width={120} height={20} fill="#1A2233" /><rect x={0} y={-150} width={20} height={150} fill="#1A2233" />
      <rect x={0} y={20} width={14} height={140} fill="#1A2233" /><rect x={106} y={20} width={14} height={140} fill="#1A2233" />
    </g>
    {v === 'fan' ? <g transform={`translate(560 70) rotate(${f * 9})`}>{[0, 120, 240].map((a) => <rect key={a} x={-10} y={0} width={20} height={190} rx={10} fill="#1C2333" transform={`rotate(${a})`} />)}<circle r={26} fill="#222B3D" /></g> : null}
    {v === 'lit' ? <rect width={W0} height={H0} fill="#E8C98A" opacity={0.07} /> : null}
  </>);
};

const PhoneClock: React.FC = () => (
  <><rect width={W0} height={H0} fill="#03050A" />
    <rect x={760} y={170} width={400} height={760} rx={60} fill="#0D1220" stroke="#2A3350" strokeWidth={6} />
    <text x={960} y={560} textAnchor="middle" fontFamily="Space Grotesk, sans-serif" fontWeight={700} fontSize={150} fill="#DDE3F0">2:10</text>
    <text x={960} y={630} textAnchor="middle" fontFamily="Inter, sans-serif" fontWeight={700} fontSize={36} fill="#7E89A6">AM</text></>
);

const Shop: React.FC = () => {
  const f = useCurrentFrame(); const up = interpolate(f, [10, 70], [0, 260], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (<><rect width={W0} height={H0} fill="#5E646E" /><rect x={460} y={200} width={1000} height={700} fill="#2C3038" />
    <g transform={`translate(0 ${-up})`}>{Array.from({length: 22}, (_, i) => <rect key={i} x={460} y={200 + i * 32} width={1000} height={26} fill="#7D838E" />)}</g>
    <rect x={420} y={150} width={1080} height={60} fill="#454A54" /></>);
};

const Tea: React.FC = () => {
  const f = useCurrentFrame();
  return (<><defs><linearGradient id="dusk" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#2A1A22" /><stop offset="100%" stopColor="#0B0D14" /></linearGradient></defs>
    <rect width={W0} height={H0} fill="url(#dusk)" />
    <rect x={560} y={640} width={800} height={60} fill="#1A1414" /><rect x={600} y={700} width={720} height={260} fill="#120E10" />
    <path d="M880,640 C860,560 900,520 960,520 C1020,520 1060,560 1040,640 Z" fill="#0A0808" /><rect x={1035} y={560} width={70} height={14} rx={7} fill="#0A0808" />
    <circle cx={960} cy={660} r={70} fill="#E07A2E" opacity={0.25} />
    {[0, 1, 2].map((i) => { const y = 480 - ((f * 1.2 + i * 60) % 180); return <path key={i} d={`M${940 + i * 20},${y + 60} c-30,-30 30,-50 0,-80`} stroke="#C9CCD3" strokeWidth={5} fill="none" opacity={0.25 * (1 - (480 - y) / 180)} />; })}</>);
};

const Stairs: React.FC = () => {
  const f = useCurrentFrame(); const fl = flicker(f, 'torch'); const sway = Math.sin(f / 12) * 30;
  return (<><rect width={W0} height={H0} fill="#06080D" />
    {Array.from({length: 9}, (_, i) => <polygon key={i} points={`${560 + i * 40},${980 - i * 95} ${1360 - i * 40},${980 - i * 95} ${1340 - i * 40},${1000 - i * 95 - 30} ${580 + i * 40},${1000 - i * 95 - 30}`} fill="#121722" stroke="#1C2230" strokeWidth={3} />)}
    <defs><radialGradient id="torch" cx="50%" cy="50%" r="50%"><stop offset="0%" stopColor="#FFF3D6" stopOpacity={0.55 * fl} /><stop offset="100%" stopColor="#FFF3D6" stopOpacity={0} /></radialGradient></defs>
    <ellipse cx={960 + sway} cy={560} rx={420} ry={360} fill="url(#torch)" />
    {Array.from({length: 40}, (_, i) => <circle key={i} cx={(random(`dx${i}`) * 900 + 510 + f * 0.6 * random(`vx${i}`)) % 1400 + 260} cy={(random(`dy${i}`) * 700 + 200 + Math.sin(f / 20 + i) * 20)} r={2} fill="#FFF3D6" opacity={0.4} />)}</>);
};

const Empty: React.FC = () => (
  <><rect width={W0} height={H0} fill="#0B0E15" /><rect x={0} y={720} width={W0} height={360} fill="#151820" />
    <rect x={0} y={720} width={W0} height={360} fill="#9AA0AA" opacity={0.08} />
    {Array.from({length: 10}, (_, i) => <ellipse key={i} cx={420 + i * 120 + (i % 2) * 30} cy={1000 - i * 26} rx={22 - i} ry={11 - i * 0.5} fill="#05070B" opacity={0.7} />)}
    <rect x={1500} y={240} width={240} height={300} fill="#1A202C" stroke="#232A38" strokeWidth={20} /><rect x={1500} y={240} width={240} height={300} fill="#C9CCD3" opacity={0.3} /></>
);

const Pov: React.FC = () => {
  const f = useCurrentFrame(); const wipe = interpolate(f, [10, 70], [0, 330], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (<><rect width={W0} height={H0} fill="#06080D" />
    <rect x={560} y={160} width={800} height={760} fill="#0E1320" stroke="#1E2433" strokeWidth={30} />
    <rect x={700} y={300} width={520} height={480} fill="#1A1F2C" />
    <rect x={740} y={620} width={440} height={120} rx={16} fill="#2A3142" /><rect x={760} y={590} width={130} height={50} rx={20} fill="#343C50" />
    <Figure x={980} y={590} s={0.55} pose="comb" />
    <defs><mask id="wipe"><rect width={W0} height={H0} fill="white" /><circle cx={960} cy={540} r={wipe} fill="black" /></mask></defs>
    <rect x={560} y={160} width={800} height={760} fill="#BFC4CE" opacity={0.75} mask="url(#wipe)" /></>);
};

const Mirror: React.FC<{d: number}> = ({d}) => {
  const f = useCurrentFrame();
  const lightsOut = interpolate(f, [d - 70, d - 66], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (<><rect width={W0} height={H0} fill="#05070D" />
    <g opacity={lightsOut}><Window x={760} y={260} w={400} h={480} state="mirror">
      <g fill={H.fig}><rect x={860} y={560} width={200} height={200} rx={30} /><circle cx={960} cy={520} r={52} /></g>
      <g fill={H.fig} opacity={0.95}><circle cx={1040} cy={470} r={34} /><path d="M1000,470 C1000,540 1015,600 1020,660 L1075,660 C1080,600 1085,540 1080,470 Z" /></g>
    </Window></g></>);
};

const Black: React.FC = () => <rect width={W0} height={H0} fill="#000" />;

const MAP: Record<string, (p: any) => React.ReactNode> = {
  narrow_lane_night: () => <Lane state="off" pose="none" />,
  room_interior_fan: () => <Room v="fan" />,
  phone_clock: () => <PhoneClock />,
  opposite_window_silhouette_combing: () => <Lane state="on" pose="comb" />,
  morning_shop_shutter: () => <Shop />,
  opposite_window_silhouette_wave: () => <Lane state="on" pose="wave" />,
  room_chair_turned_to_window: () => <Room v="chair" />,
  fogged_glass: () => <Room v="fog" />,
  tea_stall_dusk: () => <Tea />,
  opposite_window_figure_pointing: () => <Lane state="on" pose="point" />,
  abandoned_stairwell_torch: () => <Stairs />,
  empty_dusty_room: () => <Empty />,
  pov_through_dusty_glass_to_own_room: () => <Pov />,
  own_room_empty_bed: () => <Room v="hair" />,
  room_plain: () => <Room v="lit" />,
  opposite_window_shows_narrator_with_figure_behind: (p) => <Mirror d={p.d} />,
  black: () => <Black />,
};

// p.sequence: [[sceneName, startFraction], ...] switches scenes inside one beat.
export const AtmosScene: React.FC<SceneP> = ({p, d}) => {
  const f = useCurrentFrame();
  let name = p.scene;
  if (p.sequence) for (const [n, at] of p.sequence) if (f >= at * d) name = n;
  const draw = MAP[name] || MAP.narrow_lane_night;
  return (<svg width={W0} height={H0} viewBox={`0 0 ${W0} ${H0}`} style={{position: 'absolute', inset: 0}}>
    {draw({...p, d})}<Vignette /><Grain /></svg>);
};
