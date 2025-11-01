-- Seed data for MVP: 2 symbols
-- BTC-USD (crypto), AAPL (stock)

INSERT INTO symbols (symbol, name, asset_type, active) VALUES
    ('BTC-USD', 'Bitcoin', 'crypto', true),
    ('AAPL', 'Apple Inc.', 'stock', true)
ON CONFLICT (symbol) DO NOTHING;
