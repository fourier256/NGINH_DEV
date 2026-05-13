import type { BuffCard, Companion, StageInfo, UpgradeKey } from '../types';

export const stages: StageInfo[] = [
  { id: 1, name: '네온 트랙', theme: 'track', palette: { sky: '#251a46', road: '#30303d', shoulder: '#61397d', stripe: '#fff07a', accent: '#ff4fd8' } },
  { id: 2, name: '해안 질주', theme: 'sea', palette: { sky: '#1f93d1', road: '#344454', shoulder: '#16c7c4', stripe: '#ffffff', accent: '#ffd36b' } },
  { id: 3, name: '스카이 브리지', theme: 'bridge', palette: { sky: '#6b86ff', road: '#45485b', shoulder: '#dadce7', stripe: '#ffed9a', accent: '#ff785a' } },
  { id: 4, name: '설산 다운힐', theme: 'snow', palette: { sky: '#d8f5ff', road: '#5f6874', shoulder: '#f7fbff', stripe: '#bdf6ff', accent: '#52a8ff' } },
  { id: 5, name: '미드나잇 루프', theme: 'night', palette: { sky: '#070912', road: '#242432', shoulder: '#111223', stripe: '#7affff', accent: '#b54cff' } },
];

export const upgradeLabels: Record<UpgradeKey, string> = {
  maxSpeed: '최대속도',
  acceleration: '가속력',
  grip: '접지력',
  stability: '안정성',
};

export const companions: Companion[] = [
  { id: 'riko', name: '리코', outfit: '레이싱 재킷', mood: 'smile', rarity: 'N' },
  { id: 'mia', name: '미아', outfit: '네온 원피스', mood: 'happy', rarity: 'R' },
  { id: 'sera', name: '세라', outfit: '스노우 코트', mood: 'focus', rarity: 'SR' },
  { id: 'yuna', name: '유나', outfit: '블랙 레이서', mood: 'shock', rarity: 'SSR' },
];

export const buffCards: BuffCard[] = [
  { id: 'fuel-plus', title: '추가연료', description: '시작 연료 +25%', kind: 'fuel' },
  { id: 'mega-fuel', title: '대용량 탱크', description: '연료 소모 15% 감소', kind: 'fuel' },
  { id: 'super-boost', title: '슈퍼부스터', description: '부스터 3초 충전', kind: 'boost' },
  { id: 'nitro-chain', title: '니트로 체인', description: '아이템 획득 시 부스터 보너스', kind: 'boost' },
  { id: 'rest', title: '휴식', description: '차량 내구도 즉시 회복', kind: 'repair' },
  { id: 'mechanic', title: '긴급정비', description: '첫 치명 충돌 1회 방어', kind: 'shield' },
  { id: 'soft-tire', title: '소프트 타이어', description: '기름/물 패널 페널티 감소', kind: 'grip' },
  { id: 'gyro', title: '자이로 안정화', description: '슬립 회복 확률 증가', kind: 'grip' },
  { id: 'coin-rush', title: '코인 러시', description: '획득 코인 +40%', kind: 'score' },
  { id: 'fan-service', title: '팬서비스', description: '동승자 리액션 점수 증가', kind: 'score' },
];

export const outfits = ['레이싱 재킷', '네온 원피스', '스노우 코트', '블랙 레이서', '바캉스 드레스', '메카닉 슈트'];
