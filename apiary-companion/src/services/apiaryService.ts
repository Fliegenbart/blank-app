import { getDatabase } from '../database';
import { Apiary } from '../types';
import { generateUUID } from '../utils/uuid';

export interface CreateApiaryParams {
  userId: string;
  name: string;
  locationApprox?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  timezone?: string;
}

export async function createApiary(params: CreateApiaryParams): Promise<Apiary> {
  const db = await getDatabase();
  const id = generateUUID();
  const createdAt = new Date().toISOString();
  const timezone = params.timezone || 'Europe/Paris';

  await db.runAsync(
    `INSERT INTO apiaries (id, user_id, name, location_approx, latitude, longitude, timezone, created_at)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
    [
      id,
      params.userId,
      params.name,
      params.locationApprox || null,
      params.latitude || null,
      params.longitude || null,
      timezone,
      createdAt,
    ]
  );

  return {
    id,
    user_id: params.userId,
    name: params.name,
    location_approx: params.locationApprox || null,
    latitude: params.latitude || null,
    longitude: params.longitude || null,
    timezone,
    created_at: createdAt,
  };
}

export async function getApiary(id: string): Promise<Apiary | null> {
  const db = await getDatabase();
  const apiary = await db.getFirstAsync<Apiary>(
    'SELECT * FROM apiaries WHERE id = ?',
    [id]
  );

  return apiary || null;
}

export async function getApiariesByUser(userId: string): Promise<Apiary[]> {
  const db = await getDatabase();
  const apiaries = await db.getAllAsync<Apiary>(
    'SELECT * FROM apiaries WHERE user_id = ? ORDER BY name ASC',
    [userId]
  );

  return apiaries;
}

export async function getAllApiaries(): Promise<Apiary[]> {
  const db = await getDatabase();
  const apiaries = await db.getAllAsync<Apiary>(
    'SELECT * FROM apiaries ORDER BY created_at DESC'
  );

  return apiaries;
}

export async function updateApiary(
  id: string,
  updates: Partial<Omit<Apiary, 'id' | 'user_id' | 'created_at'>>
): Promise<void> {
  const db = await getDatabase();
  const fields: string[] = [];
  const values: any[] = [];

  if (updates.name !== undefined) {
    fields.push('name = ?');
    values.push(updates.name);
  }
  if (updates.location_approx !== undefined) {
    fields.push('location_approx = ?');
    values.push(updates.location_approx);
  }
  if (updates.latitude !== undefined) {
    fields.push('latitude = ?');
    values.push(updates.latitude);
  }
  if (updates.longitude !== undefined) {
    fields.push('longitude = ?');
    values.push(updates.longitude);
  }
  if (updates.timezone !== undefined) {
    fields.push('timezone = ?');
    values.push(updates.timezone);
  }

  if (fields.length === 0) {
    return;
  }

  values.push(id);
  const sql = `UPDATE apiaries SET ${fields.join(', ')} WHERE id = ?`;

  await db.runAsync(sql, values);
}

export async function deleteApiary(id: string): Promise<void> {
  const db = await getDatabase();
  await db.runAsync('DELETE FROM apiaries WHERE id = ?', [id]);
}

export async function getApiaryWithHivesCount(
  id: string
): Promise<(Apiary & { hives_count: number }) | null> {
  const db = await getDatabase();
  const result = await db.getFirstAsync<Apiary & { hives_count: number }>(
    `SELECT a.*, COUNT(h.id) as hives_count
     FROM apiaries a
     LEFT JOIN hives h ON a.id = h.apiary_id
     WHERE a.id = ?
     GROUP BY a.id`,
    [id]
  );

  return result || null;
}

export async function getApiariesWithHivesCounts(
  userId: string
): Promise<(Apiary & { hives_count: number })[]> {
  const db = await getDatabase();
  const results = await db.getAllAsync<Apiary & { hives_count: number }>(
    `SELECT a.*, COUNT(h.id) as hives_count
     FROM apiaries a
     LEFT JOIN hives h ON a.id = h.apiary_id
     WHERE a.user_id = ?
     GROUP BY a.id
     ORDER BY a.name ASC`,
    [userId]
  );

  return results;
}
