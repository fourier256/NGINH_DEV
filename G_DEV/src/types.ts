export type StageTheme = 'track' | 'sea' | 'bridge' | 'snow' | 'night';

export type UpgradeKey = 'maxSpeed' | 'acceleration' | 'grip' | 'stability';

export interface StageInfo {
  id: number;
  name: string;
  theme: StageTheme;
  palette: {
    sky: string;
    road: string;
    shoulder: string;
    stripe: string;
    accent: string;
  };
}

export interface UpgradeState {
  maxSpeed: number;
  acceleration: number;
  grip: number;
  stability: number;
}

export interface Companion {
  id: string;
  name: string;
  outfit: string;
  mood: 'smile' | 'happy' | 'shock' | 'focus';
  rarity: 'N' | 'R' | 'SR' | 'SSR';
}

export interface BuffCard {
  id: string;
  title: string;
  description: string;
  kind: 'fuel' | 'boost' | 'repair' | 'grip' | 'shield' | 'score';
}

export interface GameResult {
  cleared: boolean;
  distance: number;
  coins: number;
}
