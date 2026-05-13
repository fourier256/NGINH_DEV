import { useEffect, useMemo, useRef, useState } from 'react';
import type { BuffCard, Companion, GameResult, StageInfo, UpgradeState } from '../types';
import { drawGame } from '../game/Draw';
import { createInitialState, generateEnemies, generateObjects, generateRoad, updatePhysics, type GameState, type TrackObject } from '../game/Physics';
import { playSound } from '../game/Sound';

interface GameScreenProps {
  stage: StageInfo;
  upgrades: UpgradeState;
  companion: Companion;
  card?: BuffCard;
  onExit: (result: GameResult) => void;
}

export function GameScreen({ stage, upgrades, companion, card, onExit }: GameScreenProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const inputRef = useRef({ left: false, right: false, boost: false });
  const road = useMemo(() => generateRoad(stage), [stage]);
  const objectsRef = useRef<TrackObject[]>(generateObjects(stage));
  const [, forceObjectsVersion] = useState(0);
  const enemies = useMemo(() => generateEnemies(stage), [stage]);
  const stateRef = useRef<GameState>(createInitialState(upgrades, card));
  const [uiState, setUiState] = useState(stateRef.current);

  useEffect(() => {
    stateRef.current = createInitialState(upgrades, card);
    objectsRef.current = generateObjects(stage);
    forceObjectsVersion((value) => value + 1);
  }, [stage, upgrades, card]);

  useEffect(() => {
    const down = (event: KeyboardEvent) => {
      if (event.key === 'ArrowLeft' || event.key === 'a') inputRef.current.left = true;
      if (event.key === 'ArrowRight' || event.key === 'd') inputRef.current.right = true;
      if (event.key === ' ' || event.key === 'ArrowUp') inputRef.current.boost = true;
    };
    const up = (event: KeyboardEvent) => {
      if (event.key === 'ArrowLeft' || event.key === 'a') inputRef.current.left = false;
      if (event.key === 'ArrowRight' || event.key === 'd') inputRef.current.right = false;
      if (event.key === ' ' || event.key === 'ArrowUp') inputRef.current.boost = false;
    };
    window.addEventListener('keydown', down);
    window.addEventListener('keyup', up);
    return () => { window.removeEventListener('keydown', down); window.removeEventListener('keyup', up); };
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return undefined;
    const ctx = canvas.getContext('2d');
    if (!ctx) return undefined;
    let frame = 0;
    let last = performance.now();
    let done = false;

    const loop = (now: number) => {
      const dt = Math.min(0.033, (now - last) / 1000);
      last = now;
      const next = updatePhysics(stateRef.current, inputRef.current, dt, upgrades, card);
      const collided = resolveCollisions(next, objectsRef.current, (nextObjects) => { objectsRef.current = nextObjects; forceObjectsVersion((value) => value + 1); }, card);
      stateRef.current = collided;
      drawGame(ctx, stateRef.current, stage, road, objectsRef.current, enemies, card);
      if (frame % 8 === 0) setUiState(stateRef.current);
      if (!done && (stateRef.current.status === 'cleared' || stateRef.current.status === 'crashed')) {
        done = true;
        setTimeout(() => onExit({ cleared: stateRef.current.status === 'cleared', distance: stateRef.current.distance, coins: Math.floor(stateRef.current.distance * 45 + stateRef.current.coins) }), 1200);
      }
      frame += 1;
      if (!done) requestAnimationFrame(loop);
    };
    requestAnimationFrame(loop);
    return () => { done = true; };
  }, [card, enemies, onExit, road, stage, upgrades]);

  const touch = (left: boolean, active: boolean) => {
    inputRef.current[left ? 'left' : 'right'] = active;
  };

  return (
    <main className="game-shell">
      <canvas ref={canvasRef} width={420} height={760} aria-label="로드파이터 레이싱 캔버스" />
      <aside className={`pinup ${uiState.mood}`}>
        <div className={`girl ${companion.rarity.toLowerCase()}`} />
        <b>{companion.name}</b>
        <span>{uiState.mood === 'shock' ? '꺄악! 미끄러져요!' : uiState.mood === 'happy' ? '좋아요, 최고 속도!' : '집중해서 달려요!'}</span>
      </aside>
      <div className="touch-controls">
        <button onPointerDown={() => touch(true, true)} onPointerUp={() => touch(true, false)} onPointerLeave={() => touch(true, false)}>◀</button>
        <button onPointerDown={() => { inputRef.current.boost = true; playSound('boost'); }} onPointerUp={() => { inputRef.current.boost = false; }}>BOOST</button>
        <button onPointerDown={() => touch(false, true)} onPointerUp={() => touch(false, false)} onPointerLeave={() => touch(false, false)}>▶</button>
      </div>
    </main>
  );
}

function resolveCollisions(state: GameState, objects: TrackObject[], setObjects: (objects: TrackObject[]) => void, card?: BuffCard): GameState {
  const near = objects.find((obj) => !obj.hit && Math.abs(obj.z - state.distance) < 0.018 && Math.abs(obj.lane / 9 - state.playerX) < (obj.kind === 'truck' ? 0.11 : 0.07));
  if (!near) return state;
  setObjects(objects.map((obj) => obj.id === near.id ? { ...obj, hit: true } : obj));

  if (near.kind === 'coin') {
    playSound('coin');
    return { ...state, coins: state.coins + (card?.kind === 'score' ? 14 : 10), combo: state.combo + 1, mood: 'happy', message: '코인 획득!' };
  }
  if (near.kind === 'fuel') return { ...state, fuel: Math.min(130, state.fuel + 18), mood: 'happy', message: '연료 보급!' };
  if (near.kind === 'water') return { ...state, speed: state.speed * 0.72, message: '물웅덩이 감속!' };
  if (near.kind === 'oil') return { ...state, status: 'slip', slipDirection: state.playerX > 0.5 ? 1 : -1, mood: 'shock', message: 'SLIP!' };
  if (state.invincibleTimer > 0) return state;
  playSound('crash');
  if (state.lives > 1) return { ...state, lives: state.lives - 1, invincibleTimer: 1, speed: 60, status: 'spin', mood: 'shock', message: '실드 발동!' };
  return { ...state, status: 'crashed', speed: 0, mood: 'shock', message: 'CRASH!' };
}
