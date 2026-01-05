import { getDatabase } from '../database';
import { Hive } from '../types';
import { generateUUID } from '../utils/uuid';

export interface CreateHiveParams {
  apiaryId: string;
  hiveCode: string;
  hiveType?: string | null;
  startDate: string;
  status?: 'active' | 'inactive' | 'dead' | 'sold';
  notes?: string | null;
}

export async function createHive(params: CreateHiveParams): Promise<Hive> {
  const db = await getDatabase();
  const id = generateUUID();
  const createdAt = new Date().toISOString();
  const status = params.status || 'active';

  await db.runAsync(
    `INSERT INTO hives (id, apiary_id, hive_code, hive_type, start_date, status, notes, created_at)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
    [
      id,
      params.apiaryId,
      params.hiveCode,
      params.hiveType || null,
      params.startDate,
      status,
      params.notes || null,
      createdAt,
    ]
  );

  return {
    id,
    apiary_id: params.apiaryId,
    hive_code: params.hiveCode,
    hive_type: params.hiveType || null,
    start_date: params.startDate,
    status,
    notes: params.notes || null,
    created_at: createdAt,
  };
}

export async function getHive(id: string): Promise<Hive | null> {
  const db = await getDatabase();
  const hive = await db.getFirstAsync<Hive>('SELECT * FROM hives WHERE id = ?', [id]);

  return hive || null;
}

export async function getHivesByApiary(apiaryId: string): Promise<Hive[]> {
  const db = await getDatabase();
  const hives = await db.getAllAsync<Hive>(
    'SELECT * FROM hives WHERE apiary_id = ? ORDER BY hive_code ASC',
    [apiaryId]
  );

  return hives;
}

export async function getActiveHivesByApiary(apiaryId: string): Promise<Hive[]> {
  const db = await getDatabase();
  const hives = await db.getAllAsync<Hive>(
    `SELECT * FROM hives
     WHERE apiary_id = ? AND status = 'active'
     ORDER BY hive_code ASC`,
    [apiaryId]
  );

  return hives;
}

export async function getAllHives(): Promise<Hive[]> {
  const db = await getDatabase();
  const hives = await db.getAllAsync<Hive>(
    'SELECT * FROM hives ORDER BY created_at DESC'
  );

  return hives;
}

export async function updateHive(
  id: string,
  updates: Partial<Omit<Hive, 'id' | 'apiary_id' | 'created_at'>>
): Promise<void> {
  const db = await getDatabase();
  const fields: string[] = [];
  const values: any[] = [];

  if (updates.hive_code !== undefined) {
    fields.push('hive_code = ?');
    values.push(updates.hive_code);
  }
  if (updates.hive_type !== undefined) {
    fields.push('hive_type = ?');
    values.push(updates.hive_type);
  }
  if (updates.start_date !== undefined) {
    fields.push('start_date = ?');
    values.push(updates.start_date);
  }
  if (updates.status !== undefined) {
    fields.push('status = ?');
    values.push(updates.status);
  }
  if (updates.notes !== undefined) {
    fields.push('notes = ?');
    values.push(updates.notes);
  }

  if (fields.length === 0) {
    return;
  }

  values.push(id);
  const sql = `UPDATE hives SET ${fields.join(', ')} WHERE id = ?`;

  await db.runAsync(sql, values);
}

export async function deleteHive(id: string): Promise<void> {
  const db = await getDatabase();
  await db.runAsync('DELETE FROM hives WHERE id = ?', [id]);
}

export async function getHiveWithInspectionCount(
  id: string
): Promise<(Hive & { inspection_count: number }) | null> {
  const db = await getDatabase();
  const result = await db.getFirstAsync<Hive & { inspection_count: number }>(
    `SELECT h.*, COUNT(i.id) as inspection_count
     FROM hives h
     LEFT JOIN inspections i ON h.id = i.hive_id
     WHERE h.id = ?
     GROUP BY h.id`,
    [id]
  );

  return result || null;
}

export async function getHivesWithInspectionCounts(
  apiaryId: string
): Promise<(Hive & { inspection_count: number; last_inspection_date: string | null })[]> {
  const db = await getDatabase();
  const results = await db.getAllAsync<
    Hive & { inspection_count: number; last_inspection_date: string | null }
  >(
    `SELECT h.*,
            COUNT(i.id) as inspection_count,
            MAX(i.datetime) as last_inspection_date
     FROM hives h
     LEFT JOIN inspections i ON h.id = i.hive_id
     WHERE h.apiary_id = ?
     GROUP BY h.id
     ORDER BY h.hive_code ASC`,
    [apiaryId]
  );

  return results;
}

export async function updateHiveStatus(
  id: string,
  status: 'active' | 'inactive' | 'dead' | 'sold'
): Promise<void> {
  const db = await getDatabase();
  await db.runAsync('UPDATE hives SET status = ? WHERE id = ?', [status, id]);
}
