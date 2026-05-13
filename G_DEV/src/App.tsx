import { useMemo, useState } from 'react';
import { Menu } from './components/Menu';
import { rollCards, WorldMap } from './components/WorldMap';
import { GameScreen } from './components/GameScreen';
import { companions, stages } from './game/data';
import type { BuffCard, Companion, GameResult, StageInfo, UpgradeKey, UpgradeState } from './types';
import './styles.css';

type Screen = 'menu' | 'world' | 'game';

const initialUpgrades: UpgradeState = { maxSpeed: 1, acceleration: 1, grip: 1, stability: 1 };

function App() {
  const [screen, setScreen] = useState<Screen>('menu');
  const [coins, setCoins] = useState(450);
  const [unlocked, setUnlocked] = useState(1);
  const [upgrades, setUpgrades] = useState(initialUpgrades);
  const [roster, setRoster] = useState<Companion[]>([companions[0]]);
  const [companion, setCompanion] = useState<Companion>(companions[0]);
  const [cards, setCards] = useState<BuffCard[]>(() => rollCards());
  const [selectedCard, setSelectedCard] = useState<BuffCard | undefined>(cards[0]);
  const [stage, setStage] = useState<StageInfo>(stages[0]);
  const [toast, setToast] = useState('인터넷 에셋 대신 직접 제작한 CSS/SVG풍 오리지널 그래픽으로 구성했습니다.');
  const clearToast = () => window.setTimeout(() => setToast(''), 2400);

  const enhancedCompanion = useMemo(() => ({ ...companion, mood: 'smile' as const }), [companion]);

  const upgrade = (key: UpgradeKey) => {
    if (coins < 120 || upgrades[key] >= 5) return;
    setCoins((value) => value - 120);
    setUpgrades((value) => ({ ...value, [key]: Math.min(5, value[key] + 1) }));
    setToast('튜닝 성공! 성능이 향상되었습니다.');
    clearToast();
  };

  const shop = (outfit: string) => {
    if (coins < 80) return;
    setCoins((value) => value - 80);
    setCompanion((value) => ({ ...value, outfit }));
    setToast(`${outfit} 의상을 장착했습니다.`);
    clearToast();
  };

  const hunt = () => {
    if (coins < 150) return;
    setCoins((value) => value - 150);
    const roll = Math.random();
    const pool = roll > 0.96 ? companions.filter((girl) => girl.rarity === 'SSR') : roll > 0.78 ? companions.filter((girl) => girl.rarity === 'SR') : roll > 0.42 ? companions.filter((girl) => girl.rarity === 'R') : companions;
    const picked = pool[Math.floor(Math.random() * pool.length)] ?? companions[0];
    setRoster((value) => value.some((girl) => girl.id === picked.id) ? value : [...value, picked]);
    setCompanion(picked);
    setToast(`${picked.rarity} ${picked.name} 합류!`);
    clearToast();
  };

  const finishGame = (result: GameResult) => {
    const reward = result.cleared ? result.coins + 300 : result.coins;
    setCoins((value) => value + reward);
    if (result.cleared) setUnlocked((value) => Math.min(stages.length, Math.max(value, stage.id + 1)));
    setToast(result.cleared ? `${stage.name} 클리어! ${reward}C 획득` : `도전 종료 · ${reward}C 획득`);
    setScreen('world');
    setCards(rollCards());
    clearToast();
  };

  return (
    <div className="app">
      {screen === 'menu' && <Menu coins={coins} upgrades={upgrades} companion={enhancedCompanion} roster={roster} onStart={() => setScreen('world')} onUpgrade={upgrade} onShop={shop} onHunt={hunt} />}
      {screen === 'world' && <WorldMap unlocked={unlocked} selectedCards={cards} onRollCards={() => setCards(rollCards())} onChooseCard={setSelectedCard} onStage={(nextStage) => { setStage(nextStage); setScreen('game'); }} onBack={() => setScreen('menu')} />}
      {screen === 'game' && <GameScreen stage={stage} upgrades={upgrades} companion={enhancedCompanion} card={selectedCard} onExit={finishGame} />}
      {toast && <div className="toast">{toast}</div>}
    </div>
  );
}

export default App;
