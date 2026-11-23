import React from 'react';
import {Composition} from 'remotion';
import {Short, ShortProps} from './Short';
import {Thumb, ThumbProps} from './Thumb';
import {Brand, BrandProps} from './Brand';

const placeholder: ShortProps = {id: 'preview', channel: 'a-maps-data', fps: 30, width: 1080, height: 1920,
  durationInFrames: 90, audio: '', scenes: [], words: []};

export const RemotionRoot: React.FC = () => (<>
  <Composition
    id="Short"
    component={Short}
    defaultProps={placeholder}
    fps={30} width={1080} height={1920} durationInFrames={90}
    calculateMetadata={({props}) => ({
      durationInFrames: props.durationInFrames, fps: props.fps, width: props.width, height: props.height,
    })}
  />
  <Composition
    id="Thumb"
    component={Thumb}
    defaultProps={{...placeholder, thumb: {scene: 0, text: 'PREVIEW'}} as ThumbProps}
    fps={30} width={1080} height={1920} durationInFrames={1}
    calculateMetadata={({props}) => ({durationInFrames: props.durationInFrames, fps: props.fps, width: props.width, height: props.height})}
  />
  <Composition
    id="Brand"
    component={Brand}
    defaultProps={{kind: 'banner', channel: 'a-maps-data', width: 1920, height: 1080, fps: 30, name: 'Preview', scene: {type: 'kinetic', props: {text: 'X'}}} as BrandProps}
    fps={30} width={1920} height={1080} durationInFrames={240}
    calculateMetadata={({props}) => ({durationInFrames: 240, fps: props.fps, width: props.width, height: props.height})}
  />
</>);
