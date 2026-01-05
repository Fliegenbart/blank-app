import * as SQLite from 'expo-sqlite';
import { createTablesSQL, SCHEMA_VERSION, migrations } from './schema';

let db: SQLite.SQLiteDatabase | null = null;

export async function initDatabase(): Promise<SQLite.SQLiteDatabase> {
  if (db) {
    return db;
  }

  try {
    db = await SQLite.openDatabaseAsync('apiary-companion.db');
    console.log('Database opened successfully');

    // Run migrations
    await runMigrations(db);

    return db;
  } catch (error) {
    console.error('Failed to initialize database:', error);
    throw error;
  }
}

async function runMigrations(database: SQLite.SQLiteDatabase): Promise<void> {
  try {
    // Get current schema version
    const result = await database.getFirstAsync<{ version: number }>(
      'SELECT version FROM schema_version ORDER BY version DESC LIMIT 1'
    );

    const currentVersion = result?.version || 0;
    console.log('Current schema version:', currentVersion);

    // Apply pending migrations
    for (const migration of migrations) {
      if (migration.version > currentVersion) {
        console.log(`Applying migration version ${migration.version}...`);
        await database.execAsync(migration.sql);
        await database.runAsync(
          'INSERT INTO schema_version (version, applied_at) VALUES (?, ?)',
          [migration.version, new Date().toISOString()]
        );
        console.log(`Migration version ${migration.version} applied successfully`);
      }
    }

    console.log('All migrations completed');
  } catch (error) {
    // If schema_version table doesn't exist, this is a fresh database
    console.log('Fresh database detected, creating schema...');
    await database.execAsync(createTablesSQL);
    await database.runAsync(
      'INSERT INTO schema_version (version, applied_at) VALUES (?, ?)',
      [SCHEMA_VERSION, new Date().toISOString()]
    );
    console.log('Schema created successfully');
  }
}

export async function getDatabase(): Promise<SQLite.SQLiteDatabase> {
  if (!db) {
    return await initDatabase();
  }
  return db;
}

export async function closeDatabase(): Promise<void> {
  if (db) {
    await db.closeAsync();
    db = null;
    console.log('Database closed');
  }
}

export async function resetDatabase(): Promise<void> {
  if (db) {
    await db.closeAsync();
    db = null;
  }

  await SQLite.deleteDatabaseAsync('apiary-companion.db');
  console.log('Database deleted');

  await initDatabase();
  console.log('Database reset complete');
}
