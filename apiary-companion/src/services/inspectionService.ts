import { getDatabase } from '../database';
import { Inspection, InspectionFindings } from '../types';
import { generateUUID } from '../utils/uuid';

export interface CreateInspectionParams {
  hiveId: string;
  datetime: string;
  weather?: string | null;
  inspector?: string | null;
  freeformNotes?: string | null;
  voiceTranscript?: string | null;
  isStructured?: boolean;
}

export async function createInspection(params: CreateInspectionParams): Promise<Inspection> {
  const db = await getDatabase();
  const id = generateUUID();
  const createdAt = new Date().toISOString();

  await db.runAsync(
    `INSERT INTO inspections (id, hive_id, datetime, weather, inspector, freeform_notes, voice_transcript, is_structured, created_at)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    [
      id,
      params.hiveId,
      params.datetime,
      params.weather || null,
      params.inspector || null,
      params.freeformNotes || null,
      params.voiceTranscript || null,
      params.isStructured ? 1 : 0,
      createdAt,
    ]
  );

  return {
    id,
    hive_id: params.hiveId,
    datetime: params.datetime,
    weather: params.weather || null,
    inspector: params.inspector || null,
    freeform_notes: params.freeformNotes || null,
    voice_transcript: params.voiceTranscript || null,
    is_structured: params.isStructured || false,
    created_at: createdAt,
  };
}

export async function getInspection(id: string): Promise<Inspection | null> {
  const db = await getDatabase();
  const inspection = await db.getFirstAsync<Inspection>(
    'SELECT * FROM inspections WHERE id = ?',
    [id]
  );

  if (!inspection) {
    return null;
  }

  return {
    ...inspection,
    is_structured: Boolean(inspection.is_structured),
  };
}

export async function getInspectionsByHive(hiveId: string): Promise<Inspection[]> {
  const db = await getDatabase();
  const inspections = await db.getAllAsync<Inspection>(
    'SELECT * FROM inspections WHERE hive_id = ? ORDER BY datetime DESC',
    [hiveId]
  );

  return inspections.map((i) => ({
    ...i,
    is_structured: Boolean(i.is_structured),
  }));
}

export async function getRecentInspections(limit: number = 10): Promise<Inspection[]> {
  const db = await getDatabase();
  const inspections = await db.getAllAsync<Inspection>(
    'SELECT * FROM inspections ORDER BY datetime DESC LIMIT ?',
    [limit]
  );

  return inspections.map((i) => ({
    ...i,
    is_structured: Boolean(i.is_structured),
  }));
}

export async function updateInspection(
  id: string,
  updates: Partial<Omit<Inspection, 'id' | 'hive_id' | 'created_at'>>
): Promise<void> {
  const db = await getDatabase();
  const fields: string[] = [];
  const values: any[] = [];

  if (updates.datetime !== undefined) {
    fields.push('datetime = ?');
    values.push(updates.datetime);
  }
  if (updates.weather !== undefined) {
    fields.push('weather = ?');
    values.push(updates.weather);
  }
  if (updates.inspector !== undefined) {
    fields.push('inspector = ?');
    values.push(updates.inspector);
  }
  if (updates.freeform_notes !== undefined) {
    fields.push('freeform_notes = ?');
    values.push(updates.freeform_notes);
  }
  if (updates.voice_transcript !== undefined) {
    fields.push('voice_transcript = ?');
    values.push(updates.voice_transcript);
  }
  if (updates.is_structured !== undefined) {
    fields.push('is_structured = ?');
    values.push(updates.is_structured ? 1 : 0);
  }

  if (fields.length === 0) {
    return;
  }

  values.push(id);
  const sql = `UPDATE inspections SET ${fields.join(', ')} WHERE id = ?`;

  await db.runAsync(sql, values);
}

export async function deleteInspection(id: string): Promise<void> {
  const db = await getDatabase();
  await db.runAsync('DELETE FROM inspections WHERE id = ?', [id]);
}

// Inspection Findings methods

export async function createInspectionFindings(
  inspectionId: string,
  findings: Partial<Omit<InspectionFindings, 'id' | 'inspection_id'>>
): Promise<InspectionFindings> {
  const db = await getDatabase();
  const id = generateUUID();

  await db.runAsync(
    `INSERT INTO inspection_findings (
      id, inspection_id, brood_pattern, eggs_seen, queen_seen,
      stores_honey, stores_pollen, population_strength, temperament,
      swarm_signs, swarm_signs_detail, pests_observed,
      varroa_count_method, varroa_count_value, disease_flags, equipment_changes
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    [
      id,
      inspectionId,
      findings.brood_pattern || null,
      findings.eggs_seen !== undefined ? (findings.eggs_seen ? 1 : 0) : null,
      findings.queen_seen !== undefined ? (findings.queen_seen ? 1 : 0) : null,
      findings.stores_honey || null,
      findings.stores_pollen || null,
      findings.population_strength || null,
      findings.temperament || null,
      findings.swarm_signs !== undefined ? (findings.swarm_signs ? 1 : 0) : null,
      findings.swarm_signs_detail || null,
      findings.pests_observed || null,
      findings.varroa_count_method || null,
      findings.varroa_count_value || null,
      findings.disease_flags || null,
      findings.equipment_changes || null,
    ]
  );

  return {
    id,
    inspection_id: inspectionId,
    brood_pattern: findings.brood_pattern || null,
    eggs_seen: findings.eggs_seen || null,
    queen_seen: findings.queen_seen || null,
    stores_honey: findings.stores_honey || null,
    stores_pollen: findings.stores_pollen || null,
    population_strength: findings.population_strength || null,
    temperament: findings.temperament || null,
    swarm_signs: findings.swarm_signs || null,
    swarm_signs_detail: findings.swarm_signs_detail || null,
    pests_observed: findings.pests_observed || null,
    varroa_count_method: findings.varroa_count_method || null,
    varroa_count_value: findings.varroa_count_value || null,
    disease_flags: findings.disease_flags || null,
    equipment_changes: findings.equipment_changes || null,
  };
}

export async function getInspectionFindings(
  inspectionId: string
): Promise<InspectionFindings | null> {
  const db = await getDatabase();
  const findings = await db.getFirstAsync<InspectionFindings>(
    'SELECT * FROM inspection_findings WHERE inspection_id = ?',
    [inspectionId]
  );

  if (!findings) {
    return null;
  }

  return {
    ...findings,
    eggs_seen: findings.eggs_seen !== null ? Boolean(findings.eggs_seen) : null,
    queen_seen: findings.queen_seen !== null ? Boolean(findings.queen_seen) : null,
    swarm_signs: findings.swarm_signs !== null ? Boolean(findings.swarm_signs) : null,
  };
}

export async function updateInspectionFindings(
  inspectionId: string,
  updates: Partial<Omit<InspectionFindings, 'id' | 'inspection_id'>>
): Promise<void> {
  const db = await getDatabase();
  const fields: string[] = [];
  const values: any[] = [];

  if (updates.brood_pattern !== undefined) {
    fields.push('brood_pattern = ?');
    values.push(updates.brood_pattern);
  }
  if (updates.eggs_seen !== undefined) {
    fields.push('eggs_seen = ?');
    values.push(updates.eggs_seen !== null ? (updates.eggs_seen ? 1 : 0) : null);
  }
  if (updates.queen_seen !== undefined) {
    fields.push('queen_seen = ?');
    values.push(updates.queen_seen !== null ? (updates.queen_seen ? 1 : 0) : null);
  }
  if (updates.stores_honey !== undefined) {
    fields.push('stores_honey = ?');
    values.push(updates.stores_honey);
  }
  if (updates.stores_pollen !== undefined) {
    fields.push('stores_pollen = ?');
    values.push(updates.stores_pollen);
  }
  if (updates.population_strength !== undefined) {
    fields.push('population_strength = ?');
    values.push(updates.population_strength);
  }
  if (updates.temperament !== undefined) {
    fields.push('temperament = ?');
    values.push(updates.temperament);
  }
  if (updates.swarm_signs !== undefined) {
    fields.push('swarm_signs = ?');
    values.push(updates.swarm_signs !== null ? (updates.swarm_signs ? 1 : 0) : null);
  }
  if (updates.swarm_signs_detail !== undefined) {
    fields.push('swarm_signs_detail = ?');
    values.push(updates.swarm_signs_detail);
  }
  if (updates.pests_observed !== undefined) {
    fields.push('pests_observed = ?');
    values.push(updates.pests_observed);
  }
  if (updates.varroa_count_method !== undefined) {
    fields.push('varroa_count_method = ?');
    values.push(updates.varroa_count_method);
  }
  if (updates.varroa_count_value !== undefined) {
    fields.push('varroa_count_value = ?');
    values.push(updates.varroa_count_value);
  }
  if (updates.disease_flags !== undefined) {
    fields.push('disease_flags = ?');
    values.push(updates.disease_flags);
  }
  if (updates.equipment_changes !== undefined) {
    fields.push('equipment_changes = ?');
    values.push(updates.equipment_changes);
  }

  if (fields.length === 0) {
    return;
  }

  values.push(inspectionId);
  const sql = `UPDATE inspection_findings SET ${fields.join(', ')} WHERE inspection_id = ?`;

  await db.runAsync(sql, values);
}

export async function deleteInspectionFindings(inspectionId: string): Promise<void> {
  const db = await getDatabase();
  await db.runAsync('DELETE FROM inspection_findings WHERE inspection_id = ?', [
    inspectionId,
  ]);
}

export async function getInspectionWithFindings(
  id: string
): Promise<{ inspection: Inspection; findings: InspectionFindings | null } | null> {
  const inspection = await getInspection(id);
  if (!inspection) {
    return null;
  }

  const findings = await getInspectionFindings(id);

  return {
    inspection,
    findings,
  };
}
