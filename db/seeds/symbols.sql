-- Seed data for MVP: 2 symbols
-- BTC-USD (crypto), AAPL (stock)

INSERT INTO symbols (symbol, name, asset_type, active) VALUES
    ('AAPL', 'Apple Inc.', 'stock', true),
    ('BTC-USD', 'Bitcoin', 'crypto', true)
ON CONFLICT (symbol) DO NOTHING;
