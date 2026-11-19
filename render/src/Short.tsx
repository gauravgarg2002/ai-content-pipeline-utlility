import React from 'react';
import {AbsoluteFill, Audio, interpolate, Sequence, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {C, fonts, ColorCtx, buildColorMap} from './theme';
import {SCENES, Fallback} from './scenes';
import {Captions, Word} from './Captions';

export type SceneSpec = {id: string; type: string; props: any; onScreen: string | null; from: number; durationInFrames: number};
export type ShortProps = {id: string; channel: string; fps: number; width: number; height: number;
  durationInFrames: number; audio: string; scenes: SceneSpec[]; words: Word[]};

const OnScreen: React.FC<{text: string; first: boolean}> = ({text, first}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const s = first ? 1 : spring({frame: f, fps, config: {damping: 14, stiffness: 160}});
  return (
    <div style={{position: 'absolute', top: 120, left: 60, right: 60, textAlign: 'center',
      fontFamily: fonts.display, fontWeight: 700, fontSize: text.length > 22 ? 70 : 92, lineHeight: 1.05,
      letterSpacing: -1, color: C.text, transform: `scale(${0.85 + 0.15 * s})`, opacity: s,
      textShadow: '0 6px 30px rgba(0,0,0,0.6)'}}>
      {text}
    </div>
  );
};

const Camera: React.FC<{d: number; children: React.ReactNode; first: boolean}> = ({d, children, first}) => {
  const f = useCurrentFrame();
  const scale = interpolate(f, [0, d], [1, 1.05], {extrapolateRight: 'clamp'});
  const opacity = first ? 1 : interpolate(f, [0, 5], [0, 1], {extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{transform: `scale(${scale})`, opacity}}>{children}</AbsoluteFill>;
};

export const Short: React.FC<ShortProps> = ({scenes, words, audio}) => (
  <ColorCtx.Provider value={buildColorMap(scenes)}>
  <AbsoluteFill style={{background: `radial-gradient(ellipse at 50% 45%, ${C.bgGlow} 0%, ${C.bg} 70%)`}}>
    {scenes.map((sc, i) => {
      const Scene = SCENES[sc.type] || Fallback;
      return (
        <Sequence key={sc.id} from={sc.from} durationInFrames={sc.durationInFrames} name={`${sc.id} ${sc.type}`}>
          <Camera d={sc.durationInFrames} first={i === 0}>
            <Scene p={sc.props || {}} onScreen={sc.onScreen} d={sc.durationInFrames} first={i === 0} />
          </Camera>
          {sc.onScreen && sc.type !== 'kinetic_text' ? <OnScreen text={sc.onScreen} first={i === 0} /> : null}
        </Sequence>
      );
    })}
    <Captions words={words} />
    {audio ? <Audio src={staticFile(audio)} /> : null}
  </AbsoluteFill>
  </ColorCtx.Provider>
);
