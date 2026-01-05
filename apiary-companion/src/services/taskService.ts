import { getDatabase } from '../database';
import { Task } from '../types';
import { generateUUID } from '../utils/uuid';

export interface CreateTaskParams {
  apiaryId?: string | null;
  hiveId?: string | null;
  title: string;
  description?: string | null;
  dueDate?: string | null;
  priority?: 'low' | 'medium' | 'high';
  status?: 'pending' | 'completed' | 'cancelled';
  source?: 'manual' | 'inspection_suggestion' | 'seasonal_plan';
}

export async function createTask(params: CreateTaskParams): Promise<Task> {
  const db = await getDatabase();
  const id = generateUUID();
  const createdAt = new Date().toISOString();
  const priority = params.priority || 'medium';
  const status = params.status || 'pending';
  const source = params.source || 'manual';

  await db.runAsync(
    `INSERT INTO tasks (id, apiary_id, hive_id, title, description, due_date, priority, status, source, created_at, completed_at)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    [
      id,
      params.apiaryId || null,
      params.hiveId || null,
      params.title,
      params.description || null,
      params.dueDate || null,
      priority,
      status,
      source,
      createdAt,
      null,
    ]
  );

  return {
    id,
    apiary_id: params.apiaryId || null,
    hive_id: params.hiveId || null,
    title: params.title,
    description: params.description || null,
    due_date: params.dueDate || null,
    priority,
    status,
    source,
    created_at: createdAt,
    completed_at: null,
  };
}

export async function getTask(id: string): Promise<Task | null> {
  const db = await getDatabase();
  const task = await db.getFirstAsync<Task>('SELECT * FROM tasks WHERE id = ?', [id]);

  return task || null;
}

export async function getTasksByApiary(apiaryId: string): Promise<Task[]> {
  const db = await getDatabase();
  const tasks = await db.getAllAsync<Task>(
    `SELECT * FROM tasks
     WHERE apiary_id = ?
     ORDER BY
       CASE priority
         WHEN 'high' THEN 1
         WHEN 'medium' THEN 2
         WHEN 'low' THEN 3
       END,
       due_date ASC`,
    [apiaryId]
  );

  return tasks;
}

export async function getTasksByHive(hiveId: string): Promise<Task[]> {
  const db = await getDatabase();
  const tasks = await db.getAllAsync<Task>(
    `SELECT * FROM tasks
     WHERE hive_id = ?
     ORDER BY
       CASE priority
         WHEN 'high' THEN 1
         WHEN 'medium' THEN 2
         WHEN 'low' THEN 3
       END,
       due_date ASC`,
    [hiveId]
  );

  return tasks;
}

export async function getPendingTasks(): Promise<Task[]> {
  const db = await getDatabase();
  const tasks = await db.getAllAsync<Task>(
    `SELECT * FROM tasks
     WHERE status = 'pending'
     ORDER BY
       CASE priority
         WHEN 'high' THEN 1
         WHEN 'medium' THEN 2
         WHEN 'low' THEN 3
       END,
       due_date ASC`
  );

  return tasks;
}

export async function getOverdueTasks(): Promise<Task[]> {
  const db = await getDatabase();
  const now = new Date().toISOString();
  const tasks = await db.getAllAsync<Task>(
    `SELECT * FROM tasks
     WHERE status = 'pending' AND due_date < ?
     ORDER BY due_date ASC`,
    [now]
  );

  return tasks;
}

export async function getUpcomingTasks(days: number = 7): Promise<Task[]> {
  const db = await getDatabase();
  const now = new Date();
  const future = new Date(now.getTime() + days * 24 * 60 * 60 * 1000);

  const tasks = await db.getAllAsync<Task>(
    `SELECT * FROM tasks
     WHERE status = 'pending'
       AND due_date >= ?
       AND due_date <= ?
     ORDER BY due_date ASC`,
    [now.toISOString(), future.toISOString()]
  );

  return tasks;
}

export async function getAllTasks(): Promise<Task[]> {
  const db = await getDatabase();
  const tasks = await db.getAllAsync<Task>(
    'SELECT * FROM tasks ORDER BY created_at DESC'
  );

  return tasks;
}

export async function updateTask(
  id: string,
  updates: Partial<Omit<Task, 'id' | 'created_at'>>
): Promise<void> {
  const db = await getDatabase();
  const fields: string[] = [];
  const values: any[] = [];

  if (updates.apiary_id !== undefined) {
    fields.push('apiary_id = ?');
    values.push(updates.apiary_id);
  }
  if (updates.hive_id !== undefined) {
    fields.push('hive_id = ?');
    values.push(updates.hive_id);
  }
  if (updates.title !== undefined) {
    fields.push('title = ?');
    values.push(updates.title);
  }
  if (updates.description !== undefined) {
    fields.push('description = ?');
    values.push(updates.description);
  }
  if (updates.due_date !== undefined) {
    fields.push('due_date = ?');
    values.push(updates.due_date);
  }
  if (updates.priority !== undefined) {
    fields.push('priority = ?');
    values.push(updates.priority);
  }
  if (updates.status !== undefined) {
    fields.push('status = ?');
    values.push(updates.status);
  }
  if (updates.source !== undefined) {
    fields.push('source = ?');
    values.push(updates.source);
  }
  if (updates.completed_at !== undefined) {
    fields.push('completed_at = ?');
    values.push(updates.completed_at);
  }

  if (fields.length === 0) {
    return;
  }

  values.push(id);
  const sql = `UPDATE tasks SET ${fields.join(', ')} WHERE id = ?`;

  await db.runAsync(sql, values);
}

export async function completeTask(id: string): Promise<void> {
  const db = await getDatabase();
  const completedAt = new Date().toISOString();

  await db.runAsync(
    'UPDATE tasks SET status = ?, completed_at = ? WHERE id = ?',
    ['completed', completedAt, id]
  );
}

export async function cancelTask(id: string): Promise<void> {
  const db = await getDatabase();
  await db.runAsync('UPDATE tasks SET status = ? WHERE id = ?', ['cancelled', id]);
}

export async function reopenTask(id: string): Promise<void> {
  const db = await getDatabase();
  await db.runAsync('UPDATE tasks SET status = ?, completed_at = ? WHERE id = ?', [
    'pending',
    null,
    id,
  ]);
}

export async function deleteTask(id: string): Promise<void> {
  const db = await getDatabase();
  await db.runAsync('DELETE FROM tasks WHERE id = ?', [id]);
}

export async function createTasksFromSuggestions(
  suggestions: Array<{
    title: string;
    description: string;
    dueInDays: number;
    priority: 'low' | 'medium' | 'high';
  }>,
  hiveId: string,
  apiaryId?: string
): Promise<Task[]> {
  const tasks: Task[] = [];

  for (const suggestion of suggestions) {
    const dueDate = new Date();
    dueDate.setDate(dueDate.getDate() + suggestion.dueInDays);

    const task = await createTask({
      apiaryId: apiaryId || null,
      hiveId,
      title: suggestion.title,
      description: suggestion.description,
      dueDate: dueDate.toISOString(),
      priority: suggestion.priority,
      source: 'inspection_suggestion',
    });

    tasks.push(task);
  }

  return tasks;
}
