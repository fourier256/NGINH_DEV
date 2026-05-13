export type SoundCue = 'boost' | 'coin' | 'crash' | 'card' | 'engine';

let audioContext: AudioContext | null = null;

const getContext = () => {
  if (!audioContext) audioContext = new AudioContext();
  return audioContext;
};

export const playSound = (cue: SoundCue) => {
  try {
    const ctx = getContext();
    const oscillator = ctx.createOscillator();
    const gain = ctx.createGain();
    const now = ctx.currentTime;
    const frequency = cue === 'coin' ? 880 : cue === 'boost' ? 160 : cue === 'crash' ? 80 : cue === 'card' ? 520 : 110;
    oscillator.type = cue === 'crash' ? 'sawtooth' : 'triangle';
    oscillator.frequency.setValueAtTime(frequency, now);
    oscillator.frequency.exponentialRampToValueAtTime(cue === 'boost' ? 420 : Math.max(40, frequency * 0.55), now + 0.18);
    gain.gain.setValueAtTime(cue === 'engine' ? 0.015 : 0.08, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.22);
    oscillator.connect(gain).connect(ctx.destination);
    oscillator.start(now);
    oscillator.stop(now + 0.24);
  } catch {
    // Some mobile browsers block audio before a user gesture; gameplay continues silently.
  }
};
