/**
 * SignalList Component
 *
 * Table view of multiple signals with filtering/sorting.
 */

interface Signal {
  id: string;
  symbol: string;
  timestamp: string;
  signalType: 'BUY' | 'SELL' | 'HOLD';
  strength: number;
  price: number;
}

interface SignalListProps {
  signals: Signal[];
}

export default function SignalList({ signals }: SignalListProps) {
  // TODO: Implement signal list table
  // - Table headers (Symbol, Signal, Strength, Price, Time)
  // - Sortable columns
  // - Filter by signal type
  // - Pagination

  return null;
}
