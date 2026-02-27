import { BTC_TWO_YEAR_DATA } from "./btc-market-data";

/**
 * Signal Preview Data
 *
 * Realistic signal examples for the landing page hero section.
 * Automatically tied to the latest BTC market data point.
 */

// Get latest data point for realistic preview
const latestBtcData = BTC_TWO_YEAR_DATA[BTC_TWO_YEAR_DATA.length - 1];
const timestamp = new Date(`${latestBtcData.date}T22:15:00Z`); // Pipeline runs at 22:15 UTC

export interface SignalPreview {
  symbol: string;
  signalType: "BUY" | "SELL" | "HOLD";
  price: number;
  strength: number;
  updatedAt: Date;
  reasoning: string[];
}

/**
 * Realistic signal examples matching actual pipeline strategy logic
 * - BUY: Crypto momentum strategy indicators (oversold, bullish crossover)
 * - SELL: Mean reversion strategy indicators (overbought, resistance rejection)
 * - HOLD: Neutral/consolidation pattern indicators
 */
export const SIGNAL_PREVIEWS: Record<
  "BUY" | "SELL" | "HOLD",
  SignalPreview
> = {
  BUY: {
    symbol: "BTC-USD",
    signalType: "BUY",
    price: latestBtcData.close,
    strength: 78,
    updatedAt: timestamp,
    reasoning: [
      "Price broke above $88,000 resistance with strong momentum",
      "RSI(14) at 62 showing healthy bullish momentum",
      "Golden cross: 50-day EMA crossed above 200-day EMA",
      "Volume +35% above 20-day average confirms breakout",
    ],
  },
  SELL: {
    symbol: "BTC-USD",
    signalType: "SELL",
    price: latestBtcData.close,
    strength: 72,
    updatedAt: timestamp,
    reasoning: [
      "Price rejected at $92,000 resistance (tested 3 times)",
      "RSI(14) at 71 showing overbought conditions",
      "Bearish divergence forming on 4-hour chart",
      "Volume declining on rallies, -18% below 20-day average",
    ],
  },
  HOLD: {
    symbol: "BTC-USD",
    signalType: "HOLD",
    price: latestBtcData.close,
    strength: 45,
    updatedAt: timestamp,
    reasoning: [
      "Consolidating between $86k-$90k after recent breakout",
      "RSI(14) neutral at 55, cooling from overbought",
      "Mixed signals: bullish trend but momentum slowing",
      "Volume near average, awaiting direction confirmation",
    ],
  },
};

/**
 * Default signal for landing page hero section.
 * Using BUY signal as it's most compelling for conversion.
 */
export const DEFAULT_SIGNAL_PREVIEW = SIGNAL_PREVIEWS.BUY;
