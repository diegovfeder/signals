-- Seed data for MVP: 3 symbols only
-- BTC-USD, ETH-USD, TSLA

INSERT INTO symbols (symbol, name, asset_type, active) VALUES
    ('BTC-USD', 'Bitcoin', 'crypto', true),
    ('ETH-USD', 'Ethereum', 'crypto', true),
    ('TSLA', 'Tesla Inc.', 'stock', true)
ON CONFLICT (symbol) DO NOTHING;
