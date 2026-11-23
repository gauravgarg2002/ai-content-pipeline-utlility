import React from 'react';
import {interpolate, random, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {SceneP} from './common';

// Shadow-puppet theatre for the epics channel (D), in the spirit of Indian leather
// puppetry (tholu bommalata / tholpavakoothu): a lamp-lit cloth screen, translucent
// coloured leather figures with punched holes, jointed arms and visible rods.
// Everything is drawn in code. 1920x1080.

const W0 = 1920, H0 = 1080, GROUND = 930;
const INK = '#2A1206', LIGHT = '#FFE6AE', GOLD = '#E3A92B';

type Spec = {type: 'man' | 'woman' | 'monkey' | 'demon' | 'bird' | 'deer'; skin?: string; cloth?: string; top?: string;
  crown?: 'kirita' | 'jata' | 'bun' | 'tiara' | 'turban' | 'wild' | 'none'; prop?: 'bow' | 'mace' | 'sword' | 'staff' | 'oar' | 'none';
  beard?: boolean; heads?: number; hunch?: boolean; fangs?: boolean; scale?: number};

export const CAST: Record<string, Spec> = {
  Rama: {type: 'man', skin: '#3F8FAE', cloth: '#C9452A', top: GOLD, crown: 'kirita', prop: 'bow'},
  Lakshmana: {type: 'man', skin: '#D9A441', cloth: '#2E7D4F', top: '#C9452A', crown: 'kirita', prop: 'bow'},
  Sita: {type: 'woman', skin: '#E8B25A', cloth: '#B8323A', top: GOLD, crown: 'bun'},
  Dasharatha: {type: 'man', skin: '#E0A866', cloth: '#7B3FA0', top: GOLD, crown: 'kirita', beard: true},
  Kaikeyi: {type: 'woman', skin: '#E0A866', cloth: '#2E6FB0', top: GOLD, crown: 'tiara'},
  Kaushalya: {type: 'woman', skin: '#E0A866', cloth: '#C98A2A', top: '#7B3FA0', crown: 'tiara'},
  Manthara: {type: 'woman', skin: '#B88A55', cloth: '#6B6B3A', top: '#4A3A2A', crown: 'none', hunch: true},
  Bharata: {type: 'man', skin: '#C99B5A', cloth: '#B8323A', top: '#2E6FB0', crown: 'kirita'},
  Guha: {type: 'man', skin: '#8A5A35', cloth: '#3D6B8C', top: '#C98A2A', crown: 'turban', prop: 'oar'},
  Sage: {type: 'man', skin: '#D8B07A', cloth: '#E07A2E', top: '#E07A2E', crown: 'jata', beard: true, prop: 'staff'},
  Surpanakha: {type: 'woman', skin: '#5C7A3A', cloth: '#6A1E1E', top: '#2A3A1A', crown: 'wild', fangs: true},
  Ravana: {type: 'demon', skin: '#2F5E3A', cloth: '#8C1C1C', top: GOLD, crown: 'kirita', heads: 10, prop: 'sword', fangs: true},
  Vibhishana: {type: 'demon', skin: '#3A5E6E', cloth: GOLD, top: '#2E6FB0', crown: 'kirita', heads: 1},
  Hanuman: {type: 'monkey', skin: '#D27A2C', cloth: '#B8323A', top: GOLD, crown: 'kirita', prop: 'mace'},
  Sugriva: {type: 'monkey', skin: '#C9A23A', cloth: '#2E7D4F', top: GOLD, crown: 'kirita'},
  Vali: {type: 'monkey', skin: '#8C6A2A', cloth: '#6A1E1E', top: GOLD, crown: 'kirita', prop: 'mace'},
  Shabari: {type: 'woman', skin: '#9A6A40', cloth: '#8C7A3A', top: '#6B5A2A', crown: 'none', hunch: true},
  Jatayu: {type: 'bird', skin: '#7A5A3A'},
  Deer: {type: 'deer', skin: GOLD},
};

// ---- poses: [upper, fore] angles in degrees, 0 = hanging down, negative = forward/up
const POSES: Record<string, {front: [number, number]; back: [number, number]; head?: number}> = {
  stand: {front: [18, 12], back: [-14, -8]},
  bless: {front: [-55, -115], back: [-10, -6]},
  point: {front: [-85, -4], back: [-12, -10]},
  bow: {front: [-70, -30], back: [-60, -95]},
  namaste: {front: [-30, -125], back: [-24, -120]},
  sad: {front: [8, 4], back: [6, 2], head: 14},
  angry: {front: [-100, -40], back: [-30, -60]},
  plead: {front: [-60, -60], back: [-50, -50], head: 8},
  walk: {front: [18, 12], back: [-14, -8]},
  fight: {front: [-100, -30], back: [-30, -60]},
  give: {front: [-70, -20], back: [-12, -10], head: 6},
  carry: {front: [-80, -70], back: [-70, -60]},
};

const Holes: React.FC<{id: string}> = ({id}) => (
  <pattern id={id} width={22} height={22} patternUnits="userSpaceOnUse">
    <circle cx={6} cy={6} r={2.6} fill={LIGHT} /><circle cx={17} cy={17} r={2.6} fill={LIGHT} /><circle cx={17} cy={6} r={1.2} fill={LIGHT} />
  </pattern>
);

const leather = (fill?: string) => ({fill: fill || '#8A5A35', fillOpacity: 0.88, stroke: INK, strokeWidth: 5, strokeLinejoin: 'round' as const});

const Arm: React.FC<{sx: number; sy: number; a: [number, number]; skin: string; prop?: string; front?: boolean; t: number}> = ({sx, sy, a, skin, prop, front, t}) => {
  const [u, fo] = a;
  return (<g transform={`translate(${sx} ${sy}) rotate(${u})`}>
    <path d="M-13,0 L13,0 L10,92 L-10,92 Z" {...leather(skin)} />
    <rect x={-12} y={10} width={24} height={9} fill={GOLD} stroke={INK} strokeWidth={3} />
    <g transform={`translate(0 92) rotate(${fo - u * 0.15})`}>
      <path d="M-10,0 L10,0 L8,84 L-8,84 Z" {...leather(skin)} />
      <rect x={-10} y={62} width={20} height={8} fill={GOLD} stroke={INK} strokeWidth={3} />
      <circle cx={0} cy={94} r={13} {...leather(skin)} />
      {front && prop === 'bow' ? <g transform="translate(0 94) rotate(-10)"><path d="M0,-210 C70,-120 70,120 0,210" fill="none" stroke={INK} strokeWidth={11} />
        <path d="M0,-210 C70,-120 70,120 0,210" fill="none" stroke={GOLD} strokeWidth={5} /><line x1={0} y1={-210} x2={0} y2={210} stroke={INK} strokeWidth={2} /></g> : null}
      {front && prop === 'mace' ? <g transform="translate(0 94) rotate(170)"><rect x={-7} y={0} width={14} height={190} {...leather('#6B4A2A')} />
        <circle cx={0} cy={215} r={42} {...leather(GOLD)} /><circle cx={0} cy={215} r={42} fill="url(#holes)" opacity={0.6} /></g> : null}
      {front && prop === 'sword' ? <g transform="translate(0 94) rotate(160)"><path d="M-9,0 L9,0 L6,230 L0,250 L-6,230 Z" fill="#C9D2DC" fillOpacity={0.85} stroke={INK} strokeWidth={4} />
        <rect x={-26} y={-8} width={52} height={12} fill={GOLD} stroke={INK} strokeWidth={3} /></g> : null}
      {front && (prop === 'staff' || prop === 'oar') ? <g transform="translate(0 94)"><rect x={-6} y={-200} width={12} height={330} {...leather('#6B4A2A')} />
        {prop === 'oar' ? <ellipse cx={0} cy={150} rx={26} ry={60} {...leather('#6B4A2A')} /> : null}</g> : null}
    </g>
    {/* rod from the hand down below the screen, as in real puppetry */}
    <line x1={0} y1={0} x2={Math.sin(t / 40) * 6} y2={900} stroke={INK} strokeWidth={2.5} opacity={front ? 0.55 : 0.35} transform={`rotate(${-u})`} />
  </g>);
};

const Crown: React.FC<{kind?: string; x: number; y: number}> = ({kind, x, y}) => {
  if (!kind || kind === 'none') return null;
  if (kind === 'kirita') return (<g transform={`translate(${x} ${y})`}>
    <path d="M-48,0 L48,0 L40,-38 L-40,-38 Z" {...leather(GOLD)} /><path d="M-38,-38 L38,-38 L28,-80 L-28,-80 Z" {...leather(GOLD)} />
    <path d="M-26,-80 L26,-80 L8,-150 L0,-172 L-8,-150 Z" {...leather(GOLD)} />
    <path d="M-48,0 L48,0 L40,-38 L-40,-38 Z M-38,-38 L38,-38 L28,-80 L-28,-80 Z" fill="url(#holes)" opacity={0.7} />
    <circle cx={0} cy={-20} r={9} fill="#B8323A" stroke={INK} strokeWidth={3} /><path d="M-60,-6 C-80,-40 -70,-70 -52,-60" fill="none" stroke={INK} strokeWidth={5} /></g>);
  if (kind === 'tiara') return (<g transform={`translate(${x} ${y})`}><path d="M-44,0 L44,0 L30,-40 L14,-22 L0,-50 L-14,-22 L-30,-40 Z" {...leather(GOLD)} /></g>);
  if (kind === 'jata') return (<g transform={`translate(${x} ${y})`}><ellipse cx={-6} cy={-40} rx={34} ry={46} {...leather('#3A2A1A')} />
    <path d="M-30,-60 C-10,-90 20,-80 26,-50" fill="none" stroke="#7A5A3A" strokeWidth={5} /></g>);
  if (kind === 'turban') return (<g transform={`translate(${x} ${y})`}><path d="M-46,0 C-50,-60 40,-70 46,0 Z" {...leather('#C98A2A')} />
    <path d="M-40,-20 C-10,-40 20,-36 44,-14" fill="none" stroke={INK} strokeWidth={4} /></g>);
  if (kind === 'bun') return (<g transform={`translate(${x} ${y})`}><circle cx={-48} cy={-10} r={30} {...leather('#2A1A10')} />
    <circle cx={-60} cy={-28} r={10} fill="#F2F2F2" stroke={INK} strokeWidth={3} /><path d="M-40,-30 L40,-34" stroke={GOLD} strokeWidth={8} /></g>);
  if (kind === 'wild') return (<g transform={`translate(${x} ${y})`}>{[-70, -40, -10, 20, 50].map((a, i) =>
    <path key={i} d={`M0,0 C${a},-60 ${a * 1.4},-90 ${a * 1.6},-${70 + i * 8}`} fill="none" stroke="#1A120A" strokeWidth={10} strokeLinecap="round" />)}</g>);
  return null;
};

// Profile head facing right, centred on (0,0).
const Head: React.FC<{s: Spec; blink: boolean}> = ({s, blink}) => {
  const monkey = s.type === 'monkey', demon = s.type === 'demon';
  const face = monkey
    ? 'M-40,-30 C-44,-70 20,-78 40,-46 C70,-40 82,-10 72,10 C64,26 40,30 24,34 C0,44 -36,30 -40,-30 Z'
    : 'M-42,-24 C-44,-70 14,-80 38,-50 L44,-30 L66,-8 L46,-2 L52,10 L44,16 L46,26 C36,40 10,44 -10,40 C-36,34 -42,10 -42,-24 Z';
  return (<g>
    <path d={face} {...leather(s.skin)} />
    {monkey ? <ellipse cx={-30} cy={-8} rx={16} ry={22} {...leather(s.skin)} /> : null}
    <path d="M6,-26 C16,-36 34,-34 40,-24 C32,-16 16,-16 6,-26 Z" fill="#FFF6E0" stroke={INK} strokeWidth={3} />
    {!blink ? <circle cx={24} cy={-25} r={6} fill={INK} /> : <line x1={8} y1={-25} x2={40} y2={-25} stroke={INK} strokeWidth={4} />}
    {demon ? <path d="M24,8 C40,0 58,12 70,4" fill="none" stroke={INK} strokeWidth={6} /> : null}
    {s.fangs ? <path d="M38,18 L42,32 L46,18 Z" fill="#FFF6E0" stroke={INK} strokeWidth={2} /> : null}
    {!monkey ? <line x1={30} y1={-58} x2={30} y2={-40} stroke={s.type === 'woman' ? '#B8323A' : '#FFF6E0'} strokeWidth={5} /> : null}
    {s.beard ? <path d="M-6,30 C10,80 40,92 56,40 C44,52 20,50 6,30 Z" fill="#F2EEE6" fillOpacity={0.9} stroke={INK} strokeWidth={3} /> : null}
    <circle cx={-12} cy={18} r={8} fill={GOLD} stroke={INK} strokeWidth={3} />
  </g>);
};

const Humanoid: React.FC<{s: Spec; pose: string; walking: boolean; t: number}> = ({s, pose, walking, t}) => {
  const P = POSES[pose] || POSES.stand;
  const swing = walking ? Math.sin(t / 5) * 16 : 0;
  const sway = Math.sin(t / 22) * 3;
  const fight = pose === 'fight' ? Math.sin(t / 4) * 45 : 0;
  const breathe = Math.sin(t / 18) * 3;
  const woman = s.type === 'woman';
  const hunch = s.hunch ? 18 : 0;
  const blink = (t % 110) > 104;
  const front: [number, number] = [P.front[0] + fight + breathe, P.front[1] + breathe];
  const back: [number, number] = [P.back[0] - swing * 0.6, P.back[1]];
  return (<g transform={`rotate(${sway * 0.3})`}>
    {/* legs */}
    {!woman ? <>
      <g transform={`translate(-14 -130) rotate(${-swing})`}><rect x={-10} y={0} width={20} height={124} {...leather(s.skin)} /><path d="M-10,118 L36,118 L30,132 L-12,132 Z" {...leather(s.skin)} /></g>
      <g transform={`translate(14 -130) rotate(${swing})`}><rect x={-10} y={0} width={20} height={124} {...leather(s.skin)} /><path d="M-10,118 L36,118 L30,132 L-12,132 Z" {...leather(s.skin)} /></g>
      <path d="M-52,-292 L54,-292 L84,-120 L58,-132 L40,-112 L14,-128 L-14,-110 L-40,-128 L-72,-118 Z" {...leather(s.cloth)} />
      <path d="M-52,-292 L54,-292 L84,-120 L-72,-118 Z" fill="url(#holes)" opacity={0.55} />
    </> : <>
      <path d="M-50,-300 L50,-300 L86,0 L-80,0 Z" {...leather(s.cloth)} />
      <path d="M-50,-300 L50,-300 L86,0 L-80,0 Z" fill="url(#holes)" opacity={0.5} />
      <path d="M-60,-120 L80,-100" stroke={GOLD} strokeWidth={10} opacity={0.9} />
    </>}
    {/* back arm, torso, front arm */}
    <g transform={`rotate(${hunch} 0 -300)`}>
      <Arm sx={-8} sy={-452} a={back} skin={s.skin!} t={t} />
      <path d="M-46,-292 C-56,-360 -52,-430 -32,-470 L36,-470 C56,-430 52,-360 46,-292 Z" {...leather(s.skin)} />
      <path d="M-46,-292 C-50,-330 -50,-350 -48,-370 L48,-370 C50,-350 50,-330 46,-292 Z" {...leather(s.top)} />
      <path d="M-46,-292 C-50,-330 -50,-350 -48,-370 L48,-370 C50,-350 50,-330 46,-292 Z" fill="url(#holes)" opacity={0.6} />
      <path d="M-30,-462 C-10,-410 30,-410 40,-462" fill="none" stroke={GOLD} strokeWidth={9} /><path d="M-26,-450 C-6,-420 24,-420 34,-450" fill="none" stroke="#B8323A" strokeWidth={5} />
      {woman ? <path d="M-60,-470 C-90,-380 -84,-300 -70,-240" fill="none" stroke="#1A120A" strokeWidth={16} strokeLinecap="round" /> : null}
      {/* heads: Ravana's extra heads fan out behind the main one */}
      <g transform={`translate(6 ${-540 + (P.head ? 4 : 0)}) rotate(${P.head || 0})`}>
        {(s.heads || 1) > 1 ? Array.from({length: (s.heads || 1) - 1}, (_, i) => { const k = i < 4 ? -(i + 1) : i - 3;
          return <g key={i} transform={`translate(${k * 62} ${Math.abs(k) * 12}) scale(0.82)`} opacity={0.95}><Head s={s} blink={false} /><Crown kind="tiara" x={0} y={-62} /></g>; }) : null}
        <Head s={s} blink={blink} />
        <Crown kind={s.crown} x={-2} y={-64} />
      </g>
      <Arm sx={10} sy={-455} a={front} skin={s.skin!} prop={s.prop} front t={t} />
    </g>
    <line x1={0} y1={-380} x2={0} y2={500} stroke={INK} strokeWidth={4} opacity={0.5} />
  </g>);
};

const Bird: React.FC<{s: Spec; t: number; pose: string}> = ({s, t, pose}) => {
  const flap = pose === 'fall' ? 10 : Math.sin(t / 3.5) * 40;
  return (<g transform={`translate(0 -360) rotate(${pose === 'fall' ? 35 : 0})`}>
    <g transform={`rotate(${-flap})`}><path d="M-20,-10 L-260,-150 L-230,-110 L-280,-90 L-230,-70 L-270,-40 L-30,10 Z" {...leather(s.skin)} />
      <path d="M-20,-10 L-260,-150 L-280,-90 L-270,-40 L-30,10 Z" fill="url(#holes)" opacity={0.6} /></g>
    <ellipse cx={0} cy={0} rx={90} ry={44} {...leather(s.skin)} />
    <path d="M80,-20 C110,-60 150,-50 160,-24 L190,-10 L156,0 C140,10 110,10 80,10 Z" {...leather('#E8D8B8')} />
    <circle cx={140} cy={-26} r={6} fill={INK} /><path d="M-90,0 L-170,30 L-150,0 L-170,-20 Z" {...leather(s.skin)} />
    <g transform={`rotate(${flap * 0.7})`}><path d="M-10,-6 L-200,-170 L-170,-120 L-230,-110 L-170,-80 L-20,6 Z" {...leather(s.skin)} /></g>
  </g>);
};

const Deer: React.FC<{s: Spec; t: number; walking: boolean}> = ({s, t, walking}) => {
  const g = walking ? Math.sin(t / 3) * 25 : 0;
  return (<g transform="translate(0 -160)">
    {[[-60, g], [-30, -g], [50, -g], [80, g]].map(([x, a], i) => <g key={i} transform={`translate(${x} 20) rotate(${a})`}><rect x={-6} y={0} width={12} height={140} {...leather(s.skin)} /></g>)}
    <ellipse cx={10} cy={0} rx={110} ry={50} {...leather(s.skin)} /><ellipse cx={10} cy={0} rx={110} ry={50} fill="url(#holes)" opacity={0.7} />
    <path d="M100,-20 C120,-90 130,-110 150,-120 L190,-100 L160,-80 C150,-60 140,-30 120,0 Z" {...leather(s.skin)} />
    <path d="M150,-120 L140,-190 M140,-160 L110,-180 M150,-125 L180,-200 M168,-170 L200,-180" stroke={INK} strokeWidth={6} />
    <circle cx={168} cy={-106} r={5} fill={INK} />
  </g>);
};

// ---- backdrops: dark cut-out scenery in front of the lamp-lit cloth
const Backdrop: React.FC<{bg: string; t: number}> = ({bg, t}) => {
  const sil = '#1C0D04';
  const fire = bg === 'lanka' || bg === 'fire';
  return (<g>
    {bg === 'palace' ? <g fill={sil}>{[0, 1, 2, 3, 4].map((i) => <g key={i} transform={`translate(${140 + i * 410} 0)`}>
      <rect x={-20} y={420} width={40} height={510} /><path d={`M20,520 C80,430 160,430 220,520 L220,540 L20,540 Z`} />
      <path d="M-60,420 L60,420 L0,330 Z" /><circle cx={0} cy={320} r={14} /></g>)}<rect x={0} y={400} width={W0} height={30} /></g> : null}
    {bg === 'forest' || bg === 'hut' ? <g fill={sil}>
      {[160, 520, 1500, 1820].map((x, i) => <g key={i}><rect x={x - 26} y={420} width={52} height={520} />
        <ellipse cx={x} cy={380} rx={230} ry={150} /><ellipse cx={x - 120} cy={440} rx={130} ry={80} /><ellipse cx={x + 130} cy={430} rx={140} ry={90} />
        {[-140, -80, 80, 150].map((dx) => <line key={dx} x1={x + dx} y1={470} x2={x + dx} y2={720 + (dx % 3) * 20} stroke={sil} strokeWidth={4} />)}</g>)}
      {bg === 'hut' ? <g transform="translate(1180 930)"><path d="M-230,-180 L0,-360 L230,-180 Z" /><rect x={-190} y={-180} width={380} height={180} /><rect x={-50} y={-120} width={100} height={120} fill="#3A2008" /></g> : null}
    </g> : null}
    {bg === 'river' || bg === 'sea' ? <g>
      {[0, 1, 2].map((i) => <path key={i} d={`M0,${780 + i * 50} ${Array.from({length: 17}, (_, k) => `Q${k * 120 + 60},${760 + i * 50 + Math.sin(t / 10 + k + i) * 14} ${(k + 1) * 120},${780 + i * 50}`).join(' ')} L${W0},${H0} L0,${H0} Z`}
        fill={sil} opacity={0.55 + i * 0.2} />)}
      {bg === 'river' ? <g fill={sil}>{[120, 260, 1700, 1820].map((x) => <path key={x} d={`M${x},780 L${x + 10},560 L${x + 20},780 Z`} />)}</g> : null}
    </g> : null}
    {bg === 'mountains' ? <path d="M0,930 L260,520 L460,760 L760,400 L1060,800 L1320,480 L1620,760 L1920,560 L1920,930 Z" fill={sil} /> : null}
    {fire ? <g>{[200, 520, 1400, 1720].map((x, i) => <g key={i}><rect x={x - 70} y={360 + (i % 2) * 60} width={140} height={600} fill={sil} />
      <path d={`M${x - 70},${360 + (i % 2) * 60} L${x},${260 + (i % 2) * 60} L${x + 70},${360 + (i % 2) * 60} Z`} fill={sil} /></g>)}
      {Array.from({length: 14}, (_, i) => { const x = 100 + i * 135; const h = 120 + Math.sin(t / 3 + i * 1.7) * 40 + random(`f${i}`) * 60;
        return <path key={i} d={`M${x - 50},930 C${x - 40},${930 - h * 0.6} ${x - 10},${930 - h} ${x},${930 - h * 1.3} C${x + 10},${930 - h} ${x + 40},${930 - h * 0.6} ${x + 50},930 Z`} fill="#FF7A1A" opacity={0.55} />; })}</g> : null}
    {bg === 'sky' ? <g>{Array.from({length: 40}, (_, i) => <circle key={i} cx={random(`sx${i}`) * W0} cy={random(`sy${i}`) * 500 + 60} r={2 + random(`sr${i}`) * 2} fill={LIGHT} opacity={0.6 + 0.4 * Math.sin(t / 8 + i)} />)}
      <circle cx={1540} cy={220} r={90} fill="#FFF3D6" opacity={0.9} /></g> : null}
    {bg === 'court' ? <g fill={sil}><path d="M760,930 L760,620 L1160,620 L1160,930 Z" opacity={0.0} />
      <path d="M820,620 L1100,620 L1080,560 L840,560 Z M860,560 L860,430 C900,380 1020,380 1060,430 L1060,560 Z" />{[0, 1].map((i) => <rect key={i} x={i ? 1500 : 300} y={360} width={50} height={570} />)}
      <path d="M260,360 L590,360 L425,250 Z M1460,360 L1790,360 L1625,250 Z" /></g> : null}
    <rect x={0} y={GROUND} width={W0} height={H0 - GROUND} fill={sil} />
  </g>);
};

const Screen: React.FC<{t: number; fire?: boolean}> = ({t, fire}) => {
  const fl = 0.92 + 0.08 * Math.sin(t / 4) * (random(`lamp${Math.floor(t / 6)}`) > 0.7 ? 1.6 : 1);
  return (<>
    <defs><radialGradient id="lampglow" cx="50%" cy="48%" r="68%">
      <stop offset="0%" stopColor={fire ? '#FFC27A' : '#FFD99A'} stopOpacity={fl} /><stop offset="55%" stopColor={fire ? '#E0662A' : '#E09A3A'} stopOpacity={0.95} />
      <stop offset="100%" stopColor="#3A1406" stopOpacity={1} /></radialGradient>
      <pattern id="weave" width={8} height={8} patternUnits="userSpaceOnUse"><path d="M0,0 L8,0 M0,0 L0,8" stroke="#000" strokeWidth={0.6} opacity={0.18} /></pattern>
      <Holes id="holes" /></defs>
    <rect width={W0} height={H0} fill="url(#lampglow)" /><rect width={W0} height={H0} fill="url(#weave)" />
  </>);
};

const Border: React.FC = () => (<g>
  <rect x={0} y={0} width={W0} height={34} fill="#1C0D04" /><rect x={0} y={H0 - 34} width={W0} height={34} fill="#1C0D04" />
  {Array.from({length: 48}, (_, i) => <g key={i}><circle cx={20 + i * 40} cy={17} r={6} fill={GOLD} opacity={0.75} /><circle cx={20 + i * 40} cy={H0 - 17} r={6} fill={GOLD} opacity={0.75} /></g>)}
</g>);

// p: {bg, cast:[{who, x (0-1), pose, facing:'left'|'right', enter:'left'|'right'|'drop'|null, at (0-1), exit:'left'|'right'|null, exitAt, scale, walk}], label}
export const PuppetScene: React.FC<SceneP> = ({p, d}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const cast: any[] = p.cast || [];
  const fire = p.bg === 'lanka' || p.bg === 'fire';
  // slow camera drift across the stage
  const cam = interpolate(f, [0, d], [1.0, 1.05]); const pan = interpolate(f, [0, d], [0, -20]);
  return (<svg width={W0} height={H0} viewBox={`0 0 ${W0} ${H0}`} style={{position: 'absolute', inset: 0}}>
    <Screen t={f} fire={fire} />
    <g transform={`translate(${W0 / 2 + pan} ${H0 / 2}) scale(${cam}) translate(${-W0 / 2} ${-H0 / 2})`}>
      <Backdrop bg={p.bg || 'palace'} t={f} />
      {cast.map((c, i) => {
        const s = CAST[c.who] || CAST.Rama; const start = Math.round((c.at ?? 0) * d);
        const sp = spring({frame: f - start, fps, config: {damping: 200}, durationInFrames: 40});
        const x1 = (c.x ?? 0.5) * W0;
        let x = x1, y = GROUND, o = f >= start ? 1 : 0;
        if (c.enter === 'left') x = interpolate(sp, [0, 1], [-260, x1]);
        if (c.enter === 'right') x = interpolate(sp, [0, 1], [W0 + 260, x1]);
        if (c.enter === 'drop') { y = interpolate(sp, [0, 1], [GROUND - 400, GROUND]); o = sp; }
        if (c.exit) { const e = spring({frame: f - Math.round((c.exitAt ?? 0.8) * d), fps, config: {damping: 200}, durationInFrames: 40});
          x = interpolate(e, [0, 1], [x, c.exit === 'left' ? -300 : W0 + 300]); }
        const moving = (c.enter && sp < 0.98 && f >= start) || c.walk;
        const face = (c.facing || (c.x > 0.5 ? 'left' : 'right')) === 'left' ? -1 : 1;
        const sc = (c.scale || 1) * (s.type === 'bird' ? 0.9 : 1);
        const bob = moving ? Math.abs(Math.sin(f / 5)) * -10 : 0;
        return (<g key={i} opacity={o} transform={`translate(${x} ${y + bob}) scale(${face * sc} ${sc})`}>
          {s.type === 'bird' ? <Bird s={s} t={f} pose={c.pose} /> : s.type === 'deer' ? <Deer s={s} t={f} walking={!!moving} />
            : <Humanoid s={s} pose={c.pose || 'stand'} walking={!!moving} t={f + i * 13} />}
        </g>);
      })}
    </g>
    {p.label ? <g><rect x={W0 / 2 - 260} y={64} width={520} height={74} rx={10} fill="#1C0D04" opacity={0.82} />
      <text x={W0 / 2} y={114} textAnchor="middle" fontFamily="Space Grotesk, sans-serif" fontWeight={700} fontSize={40} fill={GOLD} letterSpacing={4}>{p.label}</text></g> : null}
    <Border />
  </svg>);
};
