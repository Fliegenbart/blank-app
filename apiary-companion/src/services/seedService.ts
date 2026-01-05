import { createUser, getOrCreateLocalUser } from './userService';
import { createApiary } from './apiaryService';
import { createHive } from './hiveService';
import {
  createInspection,
  createInspectionFindings,
} from './inspectionService';
import { createTask } from './taskService';
import { resetDatabase } from '../database';

export interface SeedOptions {
  resetDb?: boolean;
  includeInspections?: boolean;
  includeTasks?: boolean;
}

export async function seedDemoData(
  options: SeedOptions = {}
): Promise<{
  userId: string;
  apiaryIds: string[];
  hiveIds: string[];
  inspectionIds: string[];
  taskIds: string[];
}> {
  const {
    resetDb = false,
    includeInspections = true,
    includeTasks = true,
  } = options;

  console.log('Starting demo data seeding...');

  // Reset database if requested
  if (resetDb) {
    console.log('Resetting database...');
    await resetDatabase();
  }

  // Create or get local user
  const user = await getOrCreateLocalUser();
  console.log('User created/found:', user.id);

  // Create apiaries
  const apiary1 = await createApiary({
    userId: user.id,
    name: 'Home Garden Apiary',
    locationApprox: 'Kent, UK',
    latitude: 51.2787,
    longitude: 1.0819,
    timezone: 'Europe/London',
  });

  const apiary2 = await createApiary({
    userId: user.id,
    name: 'Meadow Apiary',
    locationApprox: 'Provence, France',
    latitude: 43.9493,
    longitude: 4.8055,
    timezone: 'Europe/Paris',
  });

  console.log('Apiaries created:', apiary1.id, apiary2.id);

  // Create hives for apiary 1
  const hive1 = await createHive({
    apiaryId: apiary1.id,
    hiveCode: 'H1',
    hiveType: 'National',
    startDate: '2024-04-15',
    status: 'active',
    notes: 'Started as a swarm collected from local tree',
  });

  const hive2 = await createHive({
    apiaryId: apiary1.id,
    hiveCode: 'H2',
    hiveType: 'National',
    startDate: '2023-05-20',
    status: 'active',
    notes: 'Strong colony, 2023 marked queen',
  });

  const hive3 = await createHive({
    apiaryId: apiary1.id,
    hiveCode: 'H3',
    hiveType: 'Langstroth',
    startDate: '2024-06-01',
    status: 'active',
    notes: 'Nuc purchased from local breeder',
  });

  // Create hives for apiary 2
  const hive4 = await createHive({
    apiaryId: apiary2.id,
    hiveCode: 'P1',
    hiveType: 'Dadant',
    startDate: '2023-03-10',
    status: 'active',
    notes: 'Established colony, Buckfast bees',
  });

  const hive5 = await createHive({
    apiaryId: apiary2.id,
    hiveCode: 'P2',
    hiveType: 'Dadant',
    startDate: '2024-04-22',
    status: 'active',
    notes: 'Split from P1 in spring',
  });

  console.log('Hives created:', hive1.id, hive2.id, hive3.id, hive4.id, hive5.id);

  const inspectionIds: string[] = [];
  const taskIds: string[] = [];

  // Create inspections if requested
  if (includeInspections) {
    // Recent inspection for hive 1
    const inspection1 = await createInspection({
      hiveId: hive1.id,
      datetime: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(), // 2 days ago
      weather: 'Sunny, 18°C, light breeze',
      inspector: 'Demo User',
      freeformNotes:
        'Queen spotted on frame 3, good laying pattern. Bees calm. Building up nicely. Added a super as they are running out of space.',
      isStructured: true,
    });

    await createInspectionFindings(inspection1.id, {
      brood_pattern: 'solid',
      eggs_seen: true,
      queen_seen: true,
      stores_honey: 3,
      stores_pollen: 4,
      population_strength: 4,
      temperament: 'calm',
      swarm_signs: false,
      equipment_changes: 'Added honey super with foundation',
    });

    inspectionIds.push(inspection1.id);

    // Older inspection for hive 2
    const inspection2 = await createInspection({
      hiveId: hive2.id,
      datetime: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(), // 7 days ago
      weather: 'Cloudy, 15°C',
      inspector: 'Demo User',
      freeformNotes:
        'Strong colony. Queen not seen but eggs and larvae present. Some defensive behavior - might need to check them again soon. Stores are low, added feed.',
      isStructured: true,
    });

    await createInspectionFindings(inspection2.id, {
      brood_pattern: 'solid',
      eggs_seen: true,
      queen_seen: false,
      stores_honey: 2,
      stores_pollen: 2,
      population_strength: 5,
      temperament: 'defensive',
      swarm_signs: false,
      equipment_changes: 'Added 1:1 sugar syrup feeder',
    });

    inspectionIds.push(inspection2.id);

    // Inspection with concerns for hive 3
    const inspection3 = await createInspection({
      hiveId: hive3.id,
      datetime: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(), // 5 days ago
      weather: 'Rainy, 12°C - quick check only',
      inspector: 'Demo User',
      freeformNotes:
        'Quick inspection due to weather. Spotted a few varroa mites on bees. Population seems weaker than expected. Need to do proper varroa count and consider treatment.',
      isStructured: true,
    });

    await createInspectionFindings(inspection3.id, {
      brood_pattern: 'spotty',
      eggs_seen: true,
      queen_seen: false,
      stores_honey: 3,
      stores_pollen: 3,
      population_strength: 2,
      temperament: 'calm',
      pests_observed: 'Varroa mites visible on several bees',
    });

    inspectionIds.push(inspection3.id);

    // Inspection for hive 4
    const inspection4 = await createInspection({
      hiveId: hive4.id,
      datetime: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(), // 10 days ago
      weather: 'Warm, 22°C, sunny',
      inspector: 'Demo User',
      freeformNotes:
        'Excellent colony. Queen marked and performing well. Lots of honey stores. Should extract soon.',
      isStructured: true,
    });

    await createInspectionFindings(inspection4.id, {
      brood_pattern: 'solid',
      eggs_seen: true,
      queen_seen: true,
      stores_honey: 5,
      stores_pollen: 4,
      population_strength: 5,
      temperament: 'calm',
      swarm_signs: false,
    });

    inspectionIds.push(inspection4.id);

    console.log('Inspections created:', inspectionIds.length);
  }

  // Create tasks if requested
  if (includeTasks) {
    // High priority task for hive 3
    const task1 = await createTask({
      hiveId: hive3.id,
      apiaryId: apiary1.id,
      title: 'Perform varroa mite count',
      description:
        'Do alcohol wash or sugar roll to get accurate varroa count. Consider treatment if > 3% infestation.',
      dueDate: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(), // 2 days from now
      priority: 'high',
      status: 'pending',
      source: 'inspection_suggestion',
    });

    const task2 = await createTask({
      hiveId: hive2.id,
      apiaryId: apiary1.id,
      title: 'Monitor temperament',
      description:
        'Check colony behavior on next inspection. If still defensive, may need to requeen.',
      dueDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(), // 7 days from now
      priority: 'medium',
      status: 'pending',
      source: 'inspection_suggestion',
    });

    const task3 = await createTask({
      hiveId: hive1.id,
      apiaryId: apiary1.id,
      title: 'Check super progress',
      description: 'Verify bees are drawing out foundation in new super.',
      dueDate: new Date(Date.now() + 10 * 24 * 60 * 60 * 1000).toISOString(), // 10 days from now
      priority: 'low',
      status: 'pending',
      source: 'inspection_suggestion',
    });

    const task4 = await createTask({
      hiveId: hive4.id,
      apiaryId: apiary2.id,
      title: 'Honey extraction',
      description: 'Extract honey from full supers. Check moisture content first.',
      dueDate: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toISOString(), // 5 days from now
      priority: 'medium',
      status: 'pending',
      source: 'manual',
    });

    const task5 = await createTask({
      apiaryId: apiary1.id,
      title: 'Order supplies',
      description: 'Order varroa treatment strips and additional foundation frames.',
      dueDate: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString(), // 14 days from now
      priority: 'medium',
      status: 'pending',
      source: 'manual',
    });

    taskIds.push(task1.id, task2.id, task3.id, task4.id, task5.id);

    console.log('Tasks created:', taskIds.length);
  }

  console.log('Demo data seeding complete!');

  return {
    userId: user.id,
    apiaryIds: [apiary1.id, apiary2.id],
    hiveIds: [hive1.id, hive2.id, hive3.id, hive4.id, hive5.id],
    inspectionIds,
    taskIds,
  };
}

/**
 * Quick seed with minimal data (useful for testing)
 */
export async function seedMinimalData(): Promise<{
  userId: string;
  apiaryId: string;
  hiveId: string;
}> {
  console.log('Seeding minimal data...');

  const user = await getOrCreateLocalUser();

  const apiary = await createApiary({
    userId: user.id,
    name: 'Test Apiary',
    timezone: 'Europe/London',
  });

  const hive = await createHive({
    apiaryId: apiary.id,
    hiveCode: 'H1',
    startDate: new Date().toISOString(),
    status: 'active',
  });

  console.log('Minimal data seeding complete!');

  return {
    userId: user.id,
    apiaryId: apiary.id,
    hiveId: hive.id,
  };
}
