import React from 'react';
import {Composition} from 'remotion';
import {Short, ShortProps} from './Short';

const placeholder: ShortProps = {id: 'preview', channel: 'a-maps-data', fps: 30, width: 1080, height: 1920,
  durationInFrames: 90, audio: '', scenes: [], words: []};

export const RemotionRoot: React.FC = () => (
  <Composition
    id="Short"
    component={Short}
    defaultProps={placeholder}
    fps={30} width={1080} height={1920} durationInFrames={90}
    calculateMetadata={({props}) => ({
      durationInFrames: props.durationInFrames, fps: props.fps, width: props.width, height: props.height,
    })}
  />
);
