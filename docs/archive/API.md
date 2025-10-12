# API Documentation

Complete reference for the Trading Signals API endpoints.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-api.vercel.app`

## Authentication

No authentication required for MVP. All endpoints are public.

---

## Endpoints

### Health Check

```http
GET /health
```

Check API health and database connection status.

**Response:**

```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

### Get All Signals

```http
GET /api/signals
```

Retrieve trading signals for all symbols.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 20 | Maximum number of signals (max: 100) |
| `offset` | integer | 0 | Number of signals to skip (pagination) |
| `signal_type` | string | - | Filter by type: BUY, SELL, HOLD |
| `min_strength` | float | - | Minimum signal strength (0-100) |

**Example Request:**

```bash
curl "http://localhost:8000/api/signals?limit=10&min_strength=70"
```

**Response:**

```json
{
  "signals": [
    {
      "id": "uuid",
      "symbol": "BTC-USD",
      "timestamp": "2025-01-20T10:00:00Z",
      "signal_type": "BUY",
      "strength": 82.5,
      "reasoning": ["RSI oversold (28)", "MACD bullish crossover"],
      "price_at_signal": 42000.50
    }
  ],
  "total": 1
}
```

---

### Get Signal by Symbol

```http
GET /api/signals/{symbol}
```

Get the latest signal for a specific symbol.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | string | Asset symbol (BTC-USD, ETH-USD, TSLA) |

**Example Request:**

```bash
curl "http://localhost:8000/api/signals/BTC-USD"
```

**Response:**

```json
{
  "id": "uuid",
  "symbol": "BTC-USD",
  "timestamp": "2025-01-20T10:00:00Z",
  "signal_type": "BUY",
  "strength": 82.5,
  "reasoning": ["RSI oversold (28)", "MACD bullish crossover"],
  "price_at_signal": 42000.50
}
```

---

### Get Signal History

```http
GET /api/signals/{symbol}/history
```

Get historical signals for a symbol.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | string | Asset symbol |

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `days` | integer | 30 | Number of days of history (max: 90) |

**Example Request:**

```bash
curl "http://localhost:8000/api/signals/BTC-USD/history?days=7"
```

**Response:**

```json
{
  "signals": [...],
  "total": 15
}
```

---

### Get Market Data

```http
GET /api/market-data/{symbol}/ohlcv
```

Get OHLCV (Open, High, Low, Close, Volume) market data.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | string | Asset symbol |

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 100 | Number of candles (max: 500) |

**Example Request:**

```bash
curl "http://localhost:8000/api/market-data/BTC-USD/ohlcv?limit=50"
```

**Response:**

```json
[
  {
    "symbol": "BTC-USD",
    "timestamp": "2025-01-20T10:00:00Z",
    "open": 42000.00,
    "high": 42500.00,
    "low": 41900.00,
    "close": 42300.00,
    "volume": 12500000
  }
]
```

---

### Get Indicators

```http
GET /api/market-data/{symbol}/indicators
```

Get calculated technical indicators (RSI, MACD).

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | string | Asset symbol |

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 100 | Number of data points (max: 500) |

**Example Request:**

```bash
curl "http://localhost:8000/api/market-data/BTC-USD/indicators?limit=50"
```

**Response:**

```json
[
  {
    "symbol": "BTC-USD",
    "timestamp": "2025-01-20T10:00:00Z",
    "rsi": 28.5,
    "macd": 120.5,
    "macd_signal": -50.2,
    "macd_histogram": 170.7
  }
]
```

---

### Subscribe to Email Alerts

```http
POST /api/subscribe
```

Subscribe an email address to receive signal notifications.

**Request Body:**

```json
{
  "email": "user@example.com"
}
```

**Example Request:**

```bash
curl -X POST "http://localhost:8000/api/subscribe" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

**Response:**

```json
{
  "message": "Successfully subscribed to signal notifications",
  "email": "user@example.com"
}
```

**Error Responses:**

- `400`: Email already subscribed
- `422`: Invalid email format

---

### Unsubscribe from Email Alerts

```http
POST /api/subscribe/unsubscribe/{token}
```

Unsubscribe using the token from email footer.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `token` | string | Unsubscribe token |

**Example Request:**

```bash
curl -X POST "http://localhost:8000/api/subscribe/unsubscribe/abc123..."
```

**Response:**

```json
{
  "message": "Successfully unsubscribed from signal notifications"
}
```

---

## Error Responses

All endpoints may return these error codes:

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid parameters |
| 404 | Not Found - Resource doesn't exist |
| 422 | Validation Error - Invalid request body |
| 500 | Internal Server Error |
| 501 | Not Implemented - Endpoint stub |

**Error Response Format:**

```json
{
  "detail": "Error message here"
}
```

---

## Rate Limiting

No rate limiting implemented in MVP.

For production, consider:

- 100 requests/minute per IP
- 1,000 requests/hour per IP

---

## CORS

CORS is enabled for all origins in development.

In production, restrict to your frontend domain:

```python
allow_origins=[
  "https://your-frontend.vercel.app"
]
```

---

## Interactive Documentation

FastAPI provides auto-generated interactive docs:

- **Swagger UI**: `http://localhost:8000/api/docs`
- **ReDoc**: `http://localhost:8000/api/redoc`

Try endpoints directly in the browser!
