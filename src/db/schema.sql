-- src/db/schema.sql
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS personajes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tipo TEXT NOT NULL,              -- GUERRERO | MAGO | ARQUERO
  nombre TEXT NOT NULL,
  nivel INTEGER NOT NULL,
  vida INTEGER NOT NULL,
  vida_max INTEGER NOT NULL,

  -- Campos opcionales según tipo
  armadura INTEGER,
  mana INTEGER,
  precision INTEGER
);

-- (Opcional) Índice / unicidad por nombre si quieres forzar no duplicados:
-- CREATE UNIQUE INDEX IF NOT EXISTS idx_personajes_nombre ON personajes(nombre);
