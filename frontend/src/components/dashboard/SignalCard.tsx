/**
 * SignalCard Component
 *
 * Display a single trading signal with BUY/SELL/HOLD type, strength, and reasoning.
 */

interface SignalCardProps {
  symbol: string;
  signalType: 'BUY' | 'SELL' | 'HOLD';
  strength: number;
  reasoning: string[];
  price: number;
}

export default function SignalCard({
  symbol,
  signalType,
  strength,
  reasoning,
  price,
}: SignalCardProps) {
  // TODO: Implement signal card UI
  // - Colored border based on signal type
  // - Large signal type text
  // - Strength score display
  // - Reasoning list
  // - Link to detail page

  return null;
}
