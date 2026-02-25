PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS personajes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tipo TEXT NOT NULL,
  nombre TEXT NOT NULL,
  nivel INTEGER NOT NULL,
  vida INTEGER NOT NULL,
  vida_max INTEGER NOT NULL,
  armadura INTEGER,
  mana INTEGER,
  precision INTEGER
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_personajes_nombre ON personajes(nombre);
