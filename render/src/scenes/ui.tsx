import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {C, fonts} from '../theme';
import {Label, SceneP, Svg, useDims, useSpringAt} from './common';

// Generic app mock-ups. Deliberately unbranded: labels only, no logos or copied UI.
const Panel: React.FC<{x: number; y: number; w: number; h: number; title?: string; children?: React.ReactNode}> = ({x, y, w, h, title, children}) => (
  <g>
    <rect x={x} y={y} width={w} height={h} rx={40} fill="#121A30" stroke="#2E3A5E" strokeWidth={3} />
    {title ? <text x={x + 44} y={y + 74} fontFamily={fonts.body} fontWeight={800} fontSize={40} fill={C.text}>{title}</text> : null}
    {title ? <line x1={x} y1={y + 112} x2={x + w} y2={y + 112} stroke="#2E3A5E" strokeWidth={2} /> : null}
    {children}
  </g>
);
const Ring: React.FC<{x: number; y: number; w: number; h: number; s: number}> = ({x, y, w, h, s}) => (
  <rect x={x - 12} y={y - 12} width={w + 24} height={h + 24} rx={30} fill="none" stroke={C.accent} strokeWidth={7} opacity={s}
    strokeDasharray={`${s * 2000} 2000`} />
);
const Pill: React.FC<{x: number; y: number; w: number; h: number; text: string; fill?: string; color?: string; size?: number}> = ({x, y, w, h, text, fill = '#1F2A48', color = C.text, size = 34}) => (
  <g><rect x={x} y={y} width={w} height={h} rx={h / 2} fill={fill} />
    <text x={x + w / 2} y={y + h / 2 + size * 0.35} textAnchor="middle" fontFamily={fonts.body} fontWeight={700} fontSize={size} fill={color}>{text}</text></g>
);

const Chat: React.FC<SceneP> = ({p, first}) => {
  const x = 90, y = 360, w = 900, h = 980; const s = useSpringAt(0, first); const hl = useSpringAt(18, false);
  const target = p.highlight || 'composer';
  return (<Svg><g opacity={s}>
    <Panel x={x} y={y} w={w} h={h} title={p.app || 'AI chat'}>
      <rect x={x + 330} y={y + 160} width={520} height={90} rx={36} fill="#24315A" />
      <text x={x + 370} y={y + 218} fontFamily={fonts.body} fontWeight={700} fontSize={34} fill={C.text}>{p.prompt || 'Explain this in simple words'}</text>
      {[0, 1, 2, 3].map((i) => <rect key={i} x={x + 50} y={y + 300 + i * 56} width={[760, 700, 780, 520][i]} height={26} rx={13} fill="#2B3760" />)}
      {target === 'sponsored_section' ? <g><rect x={x + 50} y={y + 560} width={800} height={150} rx={24} fill="#1A2440" stroke="#3A4870" strokeWidth={2} />
        <text x={x + 80} y={y + 606} fontFamily={fonts.body} fontWeight={700} fontSize={28} fill={C.muted}>Sponsored</text>
        <rect x={x + 80} y={y + 630} width={520} height={24} rx={12} fill="#2B3760" /><rect x={x + 80} y={y + 670} width={380} height={24} rx={12} fill="#2B3760" />
        <Ring x={x + 50} y={y + 560} w={800} h={150} s={hl} /></g> : null}
      <rect x={x + 40} y={y + h - 170} width={w - 80} height={120} rx={60} fill="#1F2A48" />
      <text x={x + 100} y={y + h - 98} fontFamily={fonts.body} fontWeight={600} fontSize={32} fill={C.muted}>Ask anything</text>
      <Pill x={x + w - 330} y={y + h - 145} w={170} h={70} text="Think" fill={target === 'think_button' ? '#3A3220' : '#2B3760'} color={target === 'think_button' ? C.accent : C.text} />
      <circle cx={x + w - 100} cy={y + h - 110} r={38} fill={C.text} />
      {target === 'composer' ? <Ring x={x + 40} y={y + h - 170} w={w - 80} h={120} s={hl} /> : null}
      {target === 'think_button' ? <Ring x={x + w - 330} y={y + h - 145} w={170} h={70} s={hl} /> : null}
    </Panel></g></Svg>);
};

const Toggle: React.FC<{x: number; y: number; on: number}> = ({x, y, on}) => (
  <g><rect x={x} y={y} width={150} height={84} rx={42} fill={on > 0.5 ? C.second : '#3A4870'} />
    <circle cx={x + 42 + on * 66} cy={y + 42} r={32} fill={C.text} /></g>
);
const Settings: React.FC<SceneP> = ({p, d, first}) => {
  const f = useCurrentFrame(); const s = useSpringAt(0, first);
  const steps: string[] = p.path_steps || []; const label: string = p.label || 'Improve the model for everyone';
  const goingOff = p.state === 'off';
  const on = goingOff ? interpolate(f, [d * 0.4, d * 0.4 + 10], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) : 1;
  const x = 90, y = steps.length ? 560 : 520, w = 900;
  return (<Svg><g opacity={s}>
    {steps.map((st, i) => { const ss = useSpringAt(i * 12, first); return (<g key={st} opacity={ss}>
      <Pill x={90 + i * 470} y={390} w={430} h={100} text={st} fill={i === steps.length - 1 ? '#3A3220' : '#1F2A48'} color={i === steps.length - 1 ? C.accent : C.text} size={40} />
      {i < steps.length - 1 ? <text x={90 + i * 470 + 445} y={458} fontFamily={fonts.display} fontWeight={700} fontSize={50} fill={C.muted}>›</text> : null}</g>); })}
    <Panel x={x} y={y} w={w} h={520} title="Data controls">
      <text x={x + 44} y={y + 230} fontFamily={fonts.body} fontWeight={700} fontSize={38} fill={C.text}>{label}</text>
      <text x={x + 44} y={y + 285} fontFamily={fonts.body} fontWeight={600} fontSize={28} fill={C.muted}>Allow your content to be used to train models</text>
      <Toggle x={x + w - 200} y={y + 190} on={on} />
      <line x1={x + 44} y1={y + 340} x2={x + w - 44} y2={y + 340} stroke="#2E3A5E" strokeWidth={2} />
      {[0, 1].map((i) => <rect key={i} x={x + 44} y={y + 380 + i * 60} width={[560, 420][i]} height={26} rx={13} fill="#2B3760" />)}
    </Panel>
    <Label x={540} y={y + 640} text={on > 0.5 ? 'ON' : 'OFF'} size={110} color={on > 0.5 ? C.second : C.accent} />
  </g></Svg>);
};

// Icons drawn as shapes: emoji fonts are not guaranteed on the render machine.
const Icon: React.FC<{kind: string; x: number; y: number}> = ({kind, x, y}) => {
  if (kind === 'mic') return <g><rect x={x - 22} y={y - 50} width={44} height={70} rx={22} fill={C.accent} /><path d={`M${x - 40},${y} a40,40 0 0 0 80,0`} fill="none" stroke={C.accent} strokeWidth={8} /><line x1={x} y1={y + 40} x2={x} y2={y + 60} stroke={C.accent} strokeWidth={8} /></g>;
  if (kind === 'check') return <g><circle cx={x} cy={y} r={50} fill={C.second} /><path d={`M${x - 24},${y} l16,18 l34,-36`} fill="none" stroke={C.bg} strokeWidth={12} strokeLinecap="round" strokeLinejoin="round" /></g>;
  if (kind === 'gear') return <g><circle cx={x} cy={y} r={34} fill="none" stroke={C.third} strokeWidth={16} strokeDasharray="14 9" /><circle cx={x} cy={y} r={14} fill={C.third} /></g>;
  return <g><rect x={x - 40} y={y - 40} width={80} height={80} rx={20} fill={C.third} /><rect x={x - 20} y={y - 20} width={40} height={40} rx={8} fill={C.bg} /></g>;
};
const iconFor = (label: string) => (/voice|bolo|speak|prompt/i.test(label) ? 'mic' : /confirm|result|booking/i.test(label) ? 'check' : /storage|settings/i.test(label) ? 'gear' : 'app');
const Phone: React.FC<SceneP> = ({p, d, first}) => {
  const f = useCurrentFrame(); const seq: string[] = p.sequence || []; const s = useSpringAt(0, first);
  const x = 300, y = 360, w = 480, h = 980;
  const step = Math.min(seq.length - 1, Math.floor((f / Math.max(d * 0.8, 1)) * seq.length));
  return (<Svg><g opacity={s}>
    <rect x={x} y={y} width={w} height={h} rx={70} fill="#0E1528" stroke="#3A4870" strokeWidth={8} />
    <rect x={x + 180} y={y + 24} width={120} height={30} rx={15} fill="#1F2A48" />
    {seq.map((label, i) => { const sp = useSpringAt(Math.round((i / seq.length) * d * 0.8), first && i === 0); const ss = i <= step ? sp : 0;
      const yy = y + 130 + i * 260;
      return (<g key={i} opacity={ss} transform={`translate(0 ${(1 - ss) * 40})`}>
        <rect x={x + 40} y={yy} width={w - 80} height={220} rx={36} fill={i === seq.length - 1 && i === step ? '#173B3A' : '#1A2440'} stroke={i === step ? C.accent : '#2E3A5E'} strokeWidth={4} />
        <Icon kind={iconFor(label)} x={x + w / 2} y={yy + 85} />
        <text x={x + w / 2} y={yy + 180} textAnchor="middle" fontFamily={fonts.body} fontWeight={700} fontSize={30} fill={C.text}>{label}</text></g>); })}
  </g></Svg>);
};

const Devices: React.FC<SceneP> = ({p, first}) => {
  const devs: string[] = p.devices || []; const n = devs.length; const w = 260, gap = (1080 - n * w) / (n + 1);
  return (<Svg>{devs.map((dv, i) => { const s = useSpringAt(i * 10, first); const x = gap + i * (w + gap), y = 520;
    return (<g key={dv} opacity={s} transform={`translate(0 ${(1 - s) * 60})`}>
      <rect x={x} y={y} width={w} height={520} rx={44} fill="#121A30" stroke={i === 0 ? C.accent : i === 1 ? C.second : C.third} strokeWidth={7} />
      <rect x={x + 90} y={y + 22} width={80} height={20} rx={10} fill="#2E3A5E" />
      <circle cx={x + w / 2} cy={y + 270} r={60} fill="none" stroke={C.muted} strokeWidth={6} /><circle cx={x + w / 2} cy={y + 270} r={22} fill={C.muted} />
      <foreignObject x={x - 20} y={y + 560} width={w + 40} height={160}>
        <div style={{fontFamily: fonts.display, fontWeight: 700, fontSize: 34, color: C.text, textAlign: 'center', lineHeight: 1.1}}>{dv}</div>
      </foreignObject></g>); })}</Svg>);
};

const Flow: React.FC<SceneP> = ({p, first}) => {
  const a = useSpringAt(0, first), b = useSpringAt(14, first), c = useSpringAt(26, first);
  return (<Svg>
    <g opacity={a}><rect x={120} y={600} width={360} height={220} rx={50} fill="#24315A" /><text x={300} y={730} textAnchor="middle" fontFamily={fonts.body} fontWeight={800} fontSize={44} fill={C.text}>{p.from || 'Your chat'}</text></g>
    <g opacity={b}><line x1={500} y1={710} x2={560 + 60 * b} y2={710} stroke={C.accent} strokeWidth={12} strokeLinecap="round" /><path d={`M${600 + 60 * b},680 L${640 + 60 * b},710 L${600 + 60 * b},740`} fill="none" stroke={C.accent} strokeWidth={12} strokeLinecap="round" /></g>
    <g opacity={c}><rect x={680} y={580} width={300} height={260} rx={50} fill="none" stroke={C.second} strokeWidth={8} /><text x={830} y={730} textAnchor="middle" fontFamily={fonts.body} fontWeight={800} fontSize={44} fill={C.second}>{p.to || 'AI model'}</text></g>
  </Svg>);
};

const Bubbles: React.FC<SceneP> = ({p, first}) => {
  const lines: string[] = p.texts || ['नमस्ते! आज मौसम कैसा रहेगा?', 'आज धूप रहेगी, शाम को हल्की बारिश हो सकती है।', 'धन्यवाद!'];
  return (<Svg>{lines.map((t, i) => { const s = useSpringAt(i * 14, first); const mine = i % 2 === 0; const w = Math.min(860, 120 + t.length * 26);
    const x = mine ? 1000 - w : 80; const y = 480 + i * 240;
    return (<g key={i} opacity={s} transform={`translate(0 ${(1 - s) * 40})`}>
      <rect x={x} y={y} width={w} height={170} rx={44} fill={mine ? '#24315A' : '#173B3A'} />
      <foreignObject x={x + 30} y={y + 30} width={w - 60} height={130}><div style={{fontFamily: fonts.body, fontWeight: 700, fontSize: 40, color: C.text, lineHeight: 1.25}}>{t}</div></foreignObject>
    </g>); })}</Svg>);
};

const CourseCard: React.FC<SceneP> = ({p, first}) => {
  const s = useSpringAt(0, first), b = useSpringAt(16, first);
  return (<Svg><g opacity={s}>
    <Panel x={90} y={420} w={900} h={760}>
      <rect x={90} y={420} width={900} height={240} rx={40} fill="#1B2747" />
      <text x={150} y={530} fontFamily={fonts.display} fontWeight={700} fontSize={62} fill={C.text}>{p.title || 'AI Research'}</text>
      <text x={150} y={605} fontFamily={fonts.display} fontWeight={700} fontSize={62} fill={C.text}>{p.title2 || 'Foundations'}</text>
      {(p.facts || ['56 hours', 'Free', 'Badges + certificate']).map((t: string, i: number) => (
        <g key={t}><circle cx={170} cy={740 + i * 120} r={18} fill={[C.accent, C.second, C.third][i % 3]} />
          <text x={215} y={755 + i * 120} fontFamily={fonts.body} fontWeight={800} fontSize={46} fill={C.text}>{t}</text></g>))}
      <g opacity={b} transform={`translate(830 1050) rotate(-10) scale(${0.6 + 0.4 * b})`}>
        <circle r={95} fill="none" stroke={C.accent} strokeWidth={8} /><text y={18} textAnchor="middle" fontFamily={fonts.display} fontWeight={700} fontSize={50} fill={C.accent}>FREE</text></g>
    </Panel></g></Svg>);
};

export const UIScene: React.FC<SceneP> = (a) => {
  const kind = a.p.kind;
  if (kind === 'settings' || kind === 'toggle') return <Settings {...a} />;
  if (kind === 'phone') return <Phone {...a} />;
  if (kind === 'devices') return <Devices {...a} />;
  if (kind === 'flow') return <Flow {...a} />;
  if (kind === 'bubbles') return <Bubbles {...a} />;
  if (kind === 'course') return <CourseCard {...a} />;
  return <Chat {...a} />;
};
