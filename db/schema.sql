CREATE TABLE symbols(
  ticker TEXT PRIMARY KEY,
  name TEXT,
  exchange TEXT,
  currency TEXT
);

CREATE TABLE candles_daily(
  ticker TEXT,
  date TEXT,
  open REAL,
  high REAL,
  low REAL,
  close REAL,
  adj_close REAL,
  volume INTEGER,
  PRIMARY KEY (ticker, date)
);

CREATE TABLE indicators_daily(
  ticker TEXT,
  date TEXT,
  sma20 REAL,
  sma50 REAL,
  rsi14 REAL,
  macd REAL,
  macd_signal REAL,
  macd_hist REAL,
  bb_upper REAL,
  bb_mid REAL,
  bb_lower REAL,
  PRIMARY KEY (ticker, date)
);

CREATE TABLE backtests(
  id TEXT PRIMARY KEY,
  name TEXT,
  params_json TEXT,
  start TEXT,
  end TEXT,
  ticker TEXT,
  pnl REAL,
  max_dd REAL,
  sharpe REAL,
  trades INTEGER,
  win_rate REAL,
  created_at TEXT
);

CREATE TABLE portfolio_tx(
  id TEXT PRIMARY KEY,
  ticker TEXT,
  ts TEXT,
  side TEXT,
  qty REAL,
  price REAL,
  fees REAL DEFAULT 0
);

CREATE TABLE alerts(
  id TEXT PRIMARY KEY,
  ticker TEXT,
  rule TEXT,
  threshold REAL,
  active INTEGER DEFAULT 1,
  last_fired TEXT
);