-- Seed data for MVP: 4 symbols representing different asset classes
-- BTC-USD (crypto), AAPL (stocks), IVV (ETF), BRL=X (forex)

INSERT INTO symbols (symbol, name, asset_type, active) VALUES
    ('BTC-USD', 'Bitcoin', 'crypto', true),
    ('AAPL', 'Apple Inc.', 'stock', true),
    ('IVV', 'iShares Core S&P 500 ETF', 'etf', true),
    ('BRL=X', 'Brazilian Real / US Dollar', 'forex', true)
ON CONFLICT (symbol) DO NOTHING;
