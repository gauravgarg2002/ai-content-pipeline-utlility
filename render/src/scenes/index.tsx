import React from 'react';
import {SceneP} from './common';
import {GeoScene} from './geo';
import {BarsScene, CardsScene, ClocksScene, KineticScene, NumberScene, TimelineScene} from './data';
import {UIScene} from './ui';
import {DragShape, RulerScene, ShapePack, TreeScene, TrueSizeStack} from './special';
import {AtmosScene} from './horror';

export type {SceneP};
export const Fallback: React.FC<SceneP> = (a) => <KineticScene {...a} p={{text: a.onScreen || ''}} />;

export const SCENES: Record<string, React.FC<SceneP>> = {
  geo: GeoScene, number: NumberScene, bars: BarsScene, cards: CardsScene, kinetic: KineticScene, timeline: TimelineScene,
  clocks: ClocksScene, ui: UIScene, truesize: TrueSizeStack, pack: ShapePack, drag: DragShape, ruler: RulerScene,
  tree: TreeScene, atmos: AtmosScene,
};
