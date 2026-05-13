import type { Companion, UpgradeKey, UpgradeState } from '../types';
import { outfits, upgradeLabels } from '../game/data';

interface MenuProps {
  coins: number;
  upgrades: UpgradeState;
  companion: Companion;
  roster: Companion[];
  onStart: () => void;
  onUpgrade: (key: UpgradeKey) => void;
  onShop: (outfit: string) => void;
  onHunt: () => void;
}

export function Menu({ coins, upgrades, companion, roster, onStart, onUpgrade, onShop, onHunt }: MenuProps) {
  return (
    <main className="menu panel">
      <section className="hero-card">
        <p className="eyebrow">PROJECT ROAD FIGHTER REBOOT</p>
        <h1>로드파이터 리부트</h1>
        <p>세로 화면 레이싱, 로그라이크 카드 선택, 동승자 수집과 튜닝을 한 번에 즐기는 React 웹 게임 프로토타입.</p>
        <button className="primary" onClick={onStart}>출발 · 월드맵 진입</button>
      </section>

      <section className="garage-grid">
        <article className="glass">
          <h2>튜닝</h2>
          <p className="coins">보유 코인 {coins.toLocaleString()} C</p>
          {(Object.keys(upgrades) as UpgradeKey[]).map((key) => (
            <div className="upgrade" key={key}>
              <span>{upgradeLabels[key]}</span>
              <b>{'★'.repeat(upgrades[key])}{'☆'.repeat(5 - upgrades[key])}</b>
              <button onClick={() => onUpgrade(key)} disabled={coins < 120 || upgrades[key] >= 5}>강화</button>
            </div>
          ))}
        </article>

        <article className="glass">
          <h2>쇼핑</h2>
          <div className="companion-card"><div className={`girl ${companion.rarity.toLowerCase()}`} /> <div><b>{companion.name}</b><span>{companion.outfit}</span></div></div>
          <div className="chips">
            {outfits.map((outfit) => <button key={outfit} onClick={() => onShop(outfit)} disabled={coins < 80}>{outfit}</button>)}
          </div>
        </article>

        <article className="glass">
          <h2>헌팅</h2>
          <p>확률형 뽑기로 새로운 핫걸 동승자를 수집합니다. SSR은 낮은 확률로 등장합니다.</p>
          <button onClick={onHunt} disabled={coins < 150}>150C 뽑기</button>
          <div className="roster">{roster.map((girl) => <span key={girl.id}>{girl.rarity} {girl.name}</span>)}</div>
        </article>
      </section>
    </main>
  );
}
