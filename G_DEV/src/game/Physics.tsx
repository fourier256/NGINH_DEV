import type { BuffCard, StageInfo, UpgradeState } from '../types';

export type ObstacleKind = 'rock' | 'truck' | 'water' | 'oil' | 'fuel' | 'coin';
export type EnemyKind = 'green' | 'blue' | 'pink' | 'yellow' | 'black';

export interface RoadSegment {
  km: number;
  row: number[];
  center: number;
  width: number;
}

export interface TrackObject {
  id: string;
  z: number;
  lane: number;
  kind: ObstacleKind;
  hit?: boolean;
}

export interface EnemyCar {
  id: string;
  z: number;
  x: number;
  lane: number;
  kind: EnemyKind;
  speed: number;
  phase: number;
}

export interface Particle {
  id: string;
  x: number;
  y: number;
  vx: number;
  vy: number;
  life: number;
  color: string;
  size: number;
}

export interface GameState {
  distance: number;
  speed: number;
  fuel: number;
  playerX: number;
  tilt: number;
  status: 'ready' | 'running' | 'slip' | 'spin' | 'crashed' | 'cleared';
  boostTimer: number;
  invincibleTimer: number;
  slipDirection: -1 | 1;
  combo: number;
  coins: number;
  lives: number;
  mood: 'smile' | 'happy' | 'shock' | 'focus';
  message: string;
}

const clamp = (value: number, min: number, max: number) => Math.max(min, Math.min(max, value));
const rand = (seed: number) => {
  const x = Math.sin(seed * 999.91) * 10000;
  return x - Math.floor(x);
};

export const createInitialState = (upgrades: UpgradeState, card?: BuffCard): GameState => ({
  distance: 0,
  speed: 80 + upgrades.acceleration * 4,
  fuel: card?.id === 'fuel-plus' ? 125 : 100,
  playerX: 0.5,
  tilt: 0,
  status: 'running',
  boostTimer: card?.kind === 'boost' ? 3 : 0,
  invincibleTimer: 1,
  slipDirection: 1,
  combo: 0,
  coins: 0,
  lives: card?.kind === 'shield' ? 2 : 1,
  mood: 'focus',
  message: card ? `${card.title} 발동!` : 'GO!',
});

export const generateRoad = (stage: StageInfo): RoadSegment[] => {
  const result: RoadSegment[] = [];
  let center = 4.5;
  let width = stage.theme === 'bridge' ? 5 : 6;

  for (let km = 0; km < 20; km += 1) {
    for (let step = 0; step < 8; step += 1) {
      const seed = stage.id * 1000 + km * 17 + step;
      center = clamp(center + (rand(seed) - 0.5) * 1.2, 2.4, 6.6);
      width = clamp(width + Math.round((rand(seed + 4) - 0.52) * 2), 4, 8);
      const start = Math.round(center - width / 2);
      const row = Array.from({ length: 10 }, (_, lane) => (lane >= start && lane < start + width ? 1 : 0));
      result.push({ km: km + step / 8, row, center, width });
    }
  }
  return result;
};

export const generateObjects = (stage: StageInfo): TrackObject[] => {
  const objects: TrackObject[] = [];
  const kinds: ObstacleKind[] = ['rock', 'water', 'oil', 'fuel', 'coin', 'coin', 'truck'];
  for (let i = 0; i < 190; i += 1) {
    const z = 0.18 + i * 0.105 + rand(stage.id * 33 + i) * 0.05;
    const lane = Math.floor(rand(stage.id * 90 + i * 5) * 10);
    const kind = kinds[Math.floor(rand(stage.id * 55 + i * 3) * kinds.length)];
    objects.push({ id: `obj-${stage.id}-${i}`, z, lane, kind });
  }
  return objects;
};

export const generateEnemies = (stage: StageInfo): EnemyCar[] => {
  const kinds: EnemyKind[] = ['green', 'blue', 'pink', 'yellow', 'black'];
  return Array.from({ length: 65 }, (_, i) => {
    const kind = kinds[Math.floor(rand(stage.id * 80 + i) * kinds.length)];
    const speed = kind === 'black' ? 250 : kind === 'green' ? 120 : 155;
    const lane = Math.floor(rand(stage.id * 120 + i) * 8) + 1;
    return { id: `enemy-${stage.id}-${i}`, z: 0.35 + i * 0.29, x: lane / 9, lane, kind, speed, phase: rand(i + stage.id) * Math.PI * 2 };
  });
};

export const updatePhysics = (
  state: GameState,
  input: { left: boolean; right: boolean; boost: boolean },
  dt: number,
  upgrades: UpgradeState,
  card: BuffCard | undefined,
): GameState => {
  if (state.status === 'crashed' || state.status === 'cleared') return state;
  const maxSpeed = (200 + upgrades.maxSpeed * 7) * (state.boostTimer > 0 || input.boost ? 1.5 : 1);
  const grip = 0.42 + upgrades.grip * 0.06 + (card?.kind === 'grip' ? 0.12 : 0);
  const acceleration = 18 + upgrades.acceleration * 4;
  const steer = (input.left ? -1 : 0) + (input.right ? 1 : 0);
  let nextStatus = state.status;
  let slipDirection = state.slipDirection;
  let speed = clamp(state.speed + acceleration * dt, 0, maxSpeed);
  let playerX = state.playerX + steer * grip * dt;

  if (state.status === 'slip') {
    playerX += slipDirection * dt * 0.5;
    speed *= 1 - 0.08 * dt;
    if (steer === slipDirection && Math.random() < 0.3 + upgrades.stability * 0.04) nextStatus = 'running';
    if (steer === -slipDirection || steer === 0) nextStatus = Math.random() < 0.015 ? 'spin' : 'slip';
  }
  if (state.status === 'spin') {
    playerX += Math.sin(Date.now() / 80) * dt * 0.16;
    speed = Math.max(25, speed - 95 * dt);
    if (Math.random() < 0.01 + upgrades.stability * 0.002) nextStatus = 'running';
  }

  const fuelDrain = (card?.id === 'mega-fuel' ? 0.7 : 0.86) * dt * (speed / 200);
  const distance = state.distance + (speed / 3600) * dt;
  const fuel = clamp(state.fuel - fuelDrain, 0, 130);

  return {
    ...state,
    distance,
    speed: fuel <= 0 ? Math.max(0, speed - 80 * dt) : speed,
    fuel,
    playerX: clamp(playerX, 0.04, 0.96),
    tilt: steer * 10,
    status: distance >= 20 ? 'cleared' : nextStatus,
    boostTimer: Math.max(0, state.boostTimer - dt),
    invincibleTimer: Math.max(0, state.invincibleTimer - dt),
    slipDirection,
    mood: nextStatus === 'slip' || nextStatus === 'spin' ? 'shock' : speed > 220 ? 'happy' : 'focus',
    message: fuel <= 12 ? '연료 부족!' : nextStatus === 'spin' ? 'SPIN!' : state.message,
  };
};

export const projectScale = (y: number, height: number) => 0.6 + (y / height) * 0.4;
