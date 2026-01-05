import { getDatabase } from '../database';
import { User } from '../types';
import { generateUUID } from '../utils/uuid';

export async function createUser(
  email: string | null = null,
  isLocalOnly: boolean = true
): Promise<User> {
  const db = await getDatabase();
  const id = generateUUID();
  const createdAt = new Date().toISOString();
  const preferences = JSON.stringify({});

  await db.runAsync(
    `INSERT INTO users (id, email, created_at, is_local_only, preferences)
     VALUES (?, ?, ?, ?, ?)`,
    [id, email, createdAt, isLocalOnly ? 1 : 0, preferences]
  );

  return {
    id,
    email,
    created_at: createdAt,
    is_local_only: isLocalOnly,
    preferences,
  };
}

export async function getUser(id: string): Promise<User | null> {
  const db = await getDatabase();
  const user = await db.getFirstAsync<User>(
    'SELECT * FROM users WHERE id = ?',
    [id]
  );

  if (!user) {
    return null;
  }

  return {
    ...user,
    is_local_only: Boolean(user.is_local_only),
  };
}

export async function getUserByEmail(email: string): Promise<User | null> {
  const db = await getDatabase();
  const user = await db.getFirstAsync<User>(
    'SELECT * FROM users WHERE email = ?',
    [email]
  );

  if (!user) {
    return null;
  }

  return {
    ...user,
    is_local_only: Boolean(user.is_local_only),
  };
}

export async function getAllUsers(): Promise<User[]> {
  const db = await getDatabase();
  const users = await db.getAllAsync<User>('SELECT * FROM users ORDER BY created_at DESC');

  return users.map((user) => ({
    ...user,
    is_local_only: Boolean(user.is_local_only),
  }));
}

export async function getOrCreateLocalUser(): Promise<User> {
  const db = await getDatabase();
  const existingUser = await db.getFirstAsync<User>(
    'SELECT * FROM users WHERE is_local_only = 1 LIMIT 1'
  );

  if (existingUser) {
    return {
      ...existingUser,
      is_local_only: Boolean(existingUser.is_local_only),
    };
  }

  return await createUser(null, true);
}

export async function updateUserPreferences(
  id: string,
  preferences: Record<string, any>
): Promise<void> {
  const db = await getDatabase();
  const preferencesJson = JSON.stringify(preferences);

  await db.runAsync('UPDATE users SET preferences = ? WHERE id = ?', [
    preferencesJson,
    id,
  ]);
}

export async function updateUserEmail(id: string, email: string): Promise<void> {
  const db = await getDatabase();
  await db.runAsync('UPDATE users SET email = ? WHERE id = ?', [email, id]);
}

export async function deleteUser(id: string): Promise<void> {
  const db = await getDatabase();
  await db.runAsync('DELETE FROM users WHERE id = ?', [id]);
}
