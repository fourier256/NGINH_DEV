import type { BuffCard, StageInfo } from '../types';
import { projectScale, type EnemyCar, type GameState, type RoadSegment, type TrackObject } from './Physics';

const enemyColors = { green: '#4dff71', blue: '#35a7ff', pink: '#ff5bd6', yellow: '#ffe650', black: '#111111' } as const;
const obstacleColors = { rock: '#8a7b6f', truck: '#d84f43', water: '#4ed9ff', oil: '#16151f', fuel: '#54ff8a', coin: '#ffd84b' } as const;

export const drawGame = (
  ctx: CanvasRenderingContext2D,
  state: GameState,
  stage: StageInfo,
  road: RoadSegment[],
  objects: TrackObject[],
  enemies: EnemyCar[],
  card?: BuffCard,
) => {
  const { width: w, height: h } = ctx.canvas;
  ctx.clearRect(0, 0, w, h);
  const horizon = h * 0.16;
  const vanishingX = w / 2;

  const sky = ctx.createLinearGradient(0, 0, 0, h);
  sky.addColorStop(0, stage.palette.sky);
  sky.addColorStop(1, '#11131f');
  ctx.fillStyle = sky;
  ctx.fillRect(0, 0, w, h);

  drawBackdrop(ctx, stage, horizon);

  for (let i = 56; i >= 0; i -= 1) {
    const t0 = i / 56;
    const t1 = (i + 1) / 56;
    const y0 = horizon + t0 * (h - horizon);
    const y1 = horizon + t1 * (h - horizon);
    const seg = road[Math.min(road.length - 1, Math.floor((state.distance * 8 + i) % road.length))];
    const roadW0 = w * (0.18 + t0 * 0.72) * (seg.width / 7);
    const roadW1 = w * (0.18 + t1 * 0.72) * (seg.width / 7);
    const centerOffset = (seg.center - 4.5) * w * 0.015 * t1;
    ctx.fillStyle = i % 2 ? stage.palette.road : '#292b36';
    ctx.beginPath();
    ctx.moveTo(vanishingX - roadW0 / 2 + centerOffset * t0, y0);
    ctx.lineTo(vanishingX + roadW0 / 2 + centerOffset * t0, y0);
    ctx.lineTo(vanishingX + roadW1 / 2 + centerOffset, y1);
    ctx.lineTo(vanishingX - roadW1 / 2 + centerOffset, y1);
    ctx.closePath();
    ctx.fill();
    ctx.strokeStyle = stage.palette.stripe;
    ctx.globalAlpha = 0.5;
    for (let lane = 1; lane < 10; lane += 1) {
      const lx = vanishingX - roadW1 / 2 + (roadW1 / 10) * lane + centerOffset;
      ctx.beginPath();
      ctx.moveTo(vanishingX + (lx - vanishingX) * 0.62, y0);
      ctx.lineTo(lx, y1);
      ctx.stroke();
    }
    ctx.globalAlpha = 1;
  }

  const visibleObjects = objects.filter((obj) => !obj.hit && obj.z >= state.distance && obj.z < state.distance + 0.85);
  visibleObjects.forEach((obj) => drawObject(ctx, obj, (obj.z - state.distance) / 0.85, h, w));
  enemies.filter((enemy) => enemy.z >= state.distance && enemy.z < state.distance + 0.9).forEach((enemy) => drawEnemy(ctx, enemy, state, h, w));
  drawPlayer(ctx, state, w, h);
  drawFx(ctx, state, w, h);
  drawHud(ctx, state, stage, card, w, h);
};

const drawBackdrop = (ctx: CanvasRenderingContext2D, stage: StageInfo, horizon: number) => {
  const w = ctx.canvas.width;
  ctx.fillStyle = stage.palette.accent;
  ctx.globalAlpha = 0.32;
  for (let i = 0; i < 7; i += 1) {
    const x = (i / 6) * w;
    ctx.beginPath();
    ctx.moveTo(x - 80, horizon);
    ctx.lineTo(x, horizon - 55 - (i % 3) * 25);
    ctx.lineTo(x + 110, horizon);
    ctx.fill();
  }
  ctx.globalAlpha = 1;
};

const laneToX = (lane: number, y: number, w: number, h: number) => {
  const s = projectScale(y, h);
  return w / 2 + (lane / 9 - 0.5) * w * 0.78 * s;
};

const drawObject = (ctx: CanvasRenderingContext2D, obj: TrackObject, depth: number, h: number, w: number) => {
  const y = h * (0.2 + (1 - depth) ** 1.8 * 0.72);
  const s = projectScale(y, h);
  const x = laneToX(obj.lane, y, w, h);
  const size = (obj.kind === 'truck' ? 54 : 28) * s;
  ctx.fillStyle = obstacleColors[obj.kind];
  if (obj.kind === 'coin') {
    ctx.beginPath();
    ctx.ellipse(x, y, size * 0.45, size * 0.45, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#fff5a1';
    ctx.fillText('₩', x - 4, y + 4);
    return;
  }
  ctx.fillRect(x - size / 2, y - size / 2, size, size * (obj.kind === 'truck' ? 0.7 : 0.5));
};

const drawEnemy = (ctx: CanvasRenderingContext2D, enemy: EnemyCar, state: GameState, h: number, w: number) => {
  const depth = (enemy.z - state.distance) / 0.9;
  const y = h * (0.2 + (1 - depth) ** 1.7 * 0.7);
  const weave = enemy.kind === 'blue' ? Math.sin(state.distance * 18 + enemy.phase) * 0.05 : 0;
  const chase = enemy.kind === 'pink' || enemy.kind === 'yellow' || enemy.kind === 'black' ? (state.playerX - enemy.x) * 0.35 : 0;
  const x = laneToX((enemy.x + weave + chase) * 9, y, w, h);
  const s = projectScale(y, h);
  ctx.fillStyle = enemyColors[enemy.kind];
  ctx.fillRect(x - 18 * s, y - 30 * s, 36 * s, 58 * s);
  ctx.fillStyle = '#ffffff99';
  ctx.fillRect(x - 10 * s, y - 22 * s, 20 * s, 14 * s);
};

const drawPlayer = (ctx: CanvasRenderingContext2D, state: GameState, w: number, h: number) => {
  const x = w * state.playerX;
  const y = h * 0.78;
  const blink = state.invincibleTimer > 0 && Math.floor(Date.now() / 90) % 2 === 0;
  if (blink) return;
  ctx.save();
  ctx.translate(x, y);
  ctx.transform(1, 0, Math.tan((state.tilt * Math.PI) / 180), 1, 0, 0);
  ctx.fillStyle = '#ff365d';
  ctx.fillRect(-24, -50, 48, 92);
  ctx.fillStyle = '#171923';
  ctx.fillRect(-15, -34, 30, 24);
  ctx.fillStyle = '#ffe66d';
  ctx.fillRect(-20, -56, 12, 10);
  ctx.fillRect(8, -56, 12, 10);
  ctx.restore();
};

const drawFx = (ctx: CanvasRenderingContext2D, state: GameState, w: number, h: number) => {
  if (state.boostTimer > 0 || state.speed > 230) {
    ctx.strokeStyle = '#ffffff55';
    for (let i = 0; i < 20; i += 1) {
      const x = (i / 20) * w;
      ctx.beginPath();
      ctx.moveTo(w / 2, h * 0.2);
      ctx.lineTo(x, h);
      ctx.stroke();
    }
    ctx.fillStyle = '#ff8c2acc';
    ctx.beginPath();
    ctx.moveTo(w * state.playerX - 16, h * 0.84);
    ctx.lineTo(w * state.playerX, h * 0.97);
    ctx.lineTo(w * state.playerX + 16, h * 0.84);
    ctx.fill();
  }
};

const drawHud = (ctx: CanvasRenderingContext2D, state: GameState, stage: StageInfo, card: BuffCard | undefined, w: number, h: number) => {
  ctx.fillStyle = '#00000075';
  ctx.fillRect(12, 12, 116, 80);
  ctx.fillStyle = '#ffffff';
  ctx.font = '12px sans-serif';
  ctx.fillText(`${stage.name}`, 22, 34);
  ctx.fillText(`${state.distance.toFixed(2)} / 20km`, 22, 54);
  ctx.fillStyle = stage.palette.accent;
  ctx.fillRect(22, 68, (state.distance / 20) * 88, 10);

  ctx.fillStyle = '#00000080';
  ctx.fillRect(12, h - 116, 154, 98);
  ctx.fillStyle = state.fuel < 14 && Math.floor(Date.now() / 180) % 2 ? '#ff204e' : '#36ff83';
  ctx.fillRect(28, h - 96, Math.max(0, state.fuel), 12);
  ctx.strokeStyle = '#ffffff';
  ctx.beginPath();
  ctx.arc(90, h - 48, 28, Math.PI, Math.PI * 2);
  ctx.stroke();
  ctx.fillStyle = '#ffffff';
  ctx.fillText(`${Math.round(state.speed)} km/h`, 52, h - 34);
  ctx.fillText(card ? `CARD ${card.title}` : state.message, 180, 30);
};
