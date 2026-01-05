export const SCHEMA_VERSION = 1;

export const createTablesSQL = `
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  email TEXT UNIQUE,
  created_at TEXT NOT NULL,
  is_local_only INTEGER NOT NULL DEFAULT 1,
  preferences TEXT DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS apiaries (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  name TEXT NOT NULL,
  location_approx TEXT,
  latitude REAL,
  longitude REAL,
  timezone TEXT NOT NULL DEFAULT 'Europe/Paris',
  created_at TEXT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS hives (
  id TEXT PRIMARY KEY,
  apiary_id TEXT NOT NULL,
  hive_code TEXT NOT NULL,
  hive_type TEXT,
  start_date TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'active',
  notes TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY (apiary_id) REFERENCES apiaries(id) ON DELETE CASCADE,
  UNIQUE(apiary_id, hive_code)
);

CREATE TABLE IF NOT EXISTS colonies (
  id TEXT PRIMARY KEY,
  hive_id TEXT NOT NULL,
  queen_year INTEGER,
  queen_origin TEXT,
  temperament_notes TEXT,
  status TEXT NOT NULL DEFAULT 'active',
  created_at TEXT NOT NULL,
  FOREIGN KEY (hive_id) REFERENCES hives(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS inspections (
  id TEXT PRIMARY KEY,
  hive_id TEXT NOT NULL,
  datetime TEXT NOT NULL,
  weather TEXT,
  inspector TEXT,
  freeform_notes TEXT,
  voice_transcript TEXT,
  is_structured INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL,
  FOREIGN KEY (hive_id) REFERENCES hives(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS inspection_findings (
  id TEXT PRIMARY KEY,
  inspection_id TEXT NOT NULL,
  brood_pattern TEXT,
  eggs_seen INTEGER,
  queen_seen INTEGER,
  stores_honey INTEGER,
  stores_pollen INTEGER,
  population_strength INTEGER,
  temperament TEXT,
  swarm_signs INTEGER,
  swarm_signs_detail TEXT,
  pests_observed TEXT,
  varroa_count_method TEXT,
  varroa_count_value REAL,
  disease_flags TEXT,
  equipment_changes TEXT,
  FOREIGN KEY (inspection_id) REFERENCES inspections(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tasks (
  id TEXT PRIMARY KEY,
  apiary_id TEXT,
  hive_id TEXT,
  title TEXT NOT NULL,
  description TEXT,
  due_date TEXT,
  priority TEXT NOT NULL DEFAULT 'medium',
  status TEXT NOT NULL DEFAULT 'pending',
  source TEXT NOT NULL DEFAULT 'manual',
  created_at TEXT NOT NULL,
  completed_at TEXT,
  FOREIGN KEY (apiary_id) REFERENCES apiaries(id) ON DELETE CASCADE,
  FOREIGN KEY (hive_id) REFERENCES hives(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS treatments (
  id TEXT PRIMARY KEY,
  hive_id TEXT NOT NULL,
  type TEXT NOT NULL,
  product_name TEXT NOT NULL,
  start_date TEXT NOT NULL,
  end_date TEXT,
  dosage_notes TEXT,
  compliance_notes TEXT,
  effectiveness_notes TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY (hive_id) REFERENCES hives(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS harvests (
  id TEXT PRIMARY KEY,
  hive_id TEXT NOT NULL,
  date TEXT NOT NULL,
  honey_kg REAL NOT NULL,
  supers_count INTEGER,
  notes TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY (hive_id) REFERENCES hives(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS inventory_items (
  id TEXT PRIMARY KEY,
  apiary_id TEXT NOT NULL,
  category TEXT NOT NULL,
  name TEXT NOT NULL,
  quantity REAL NOT NULL,
  unit TEXT NOT NULL,
  reorder_level REAL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (apiary_id) REFERENCES apiaries(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS attachments (
  id TEXT PRIMARY KEY,
  inspection_id TEXT,
  file_path TEXT NOT NULL,
  mime_type TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (inspection_id) REFERENCES inspections(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS seasonal_plans (
  id TEXT PRIMARY KEY,
  apiary_id TEXT NOT NULL,
  region TEXT NOT NULL,
  start_month INTEGER NOT NULL,
  is_active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  FOREIGN KEY (apiary_id) REFERENCES apiaries(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS schema_version (
  version INTEGER PRIMARY KEY,
  applied_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_hives_apiary ON hives(apiary_id);
CREATE INDEX IF NOT EXISTS idx_inspections_hive ON inspections(hive_id);
CREATE INDEX IF NOT EXISTS idx_inspections_datetime ON inspections(datetime DESC);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_hive ON tasks(hive_id);
CREATE INDEX IF NOT EXISTS idx_tasks_apiary ON tasks(apiary_id);
CREATE INDEX IF NOT EXISTS idx_treatments_hive ON treatments(hive_id);
CREATE INDEX IF NOT EXISTS idx_harvests_hive ON harvests(hive_id);
`;

export const migrations = [
  {
    version: 1,
    sql: createTablesSQL,
  },
];
