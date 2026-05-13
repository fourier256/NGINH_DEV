import type { CSSProperties } from 'react';
import type { BuffCard, StageInfo } from '../types';
import { buffCards, stages } from '../game/data';

interface WorldMapProps {
  unlocked: number;
  selectedCards: BuffCard[];
  onRollCards: () => void;
  onChooseCard: (card: BuffCard) => void;
  onStage: (stage: StageInfo) => void;
  onBack: () => void;
}

export const rollCards = () => [...buffCards].sort(() => Math.random() - 0.5).slice(0, 3);

export function WorldMap({ unlocked, selectedCards, onRollCards, onChooseCard, onStage, onBack }: WorldMapProps) {
  return (
    <main className="world panel">
      <div className="topbar"><button onClick={onBack}>← 메뉴</button><h1>월드맵</h1><button onClick={onRollCards}>카드 다시 보기</button></div>
      <section className="cards">
        {selectedCards.map((card) => (
          <button className={`rogue-card ${card.kind}`} key={card.id} onClick={() => onChooseCard(card)}>
            <b>{card.title}</b><span>{card.description}</span><small>{card.kind.toUpperCase()}</small>
          </button>
        ))}
      </section>
      <section className="stage-road">
        {stages.map((stage) => (
          <button className="stage-node" key={stage.id} disabled={stage.id > unlocked} onClick={() => onStage(stage)} style={{ '--accent': stage.palette.accent } as CSSProperties}>
            <span>{stage.id}</span><b>{stage.name}</b><small>{stage.id > unlocked ? 'LOCKED' : 'READY'}</small>
          </button>
        ))}
      </section>
    </main>
  );
}
