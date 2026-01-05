import { useEffect, useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  RefreshControl,
} from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { hiveService } from '../../src/services/hiveService';
import { inspectionService } from '../../src/services/inspectionService';
import { taskService } from '../../src/services/taskService';
import { Hive, Colony, Inspection, Task } from '../../src/types';
import { format, formatDistanceToNow } from 'date-fns';

export default function HiveDetailScreen() {
  const router = useRouter();
  const { id } = useLocalSearchParams<{ id: string }>();
  const [hive, setHive] = useState<Hive | null>(null);
  const [colony, setColony] = useState<Colony | null>(null);
  const [recentInspections, setRecentInspections] = useState<Inspection[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = async () => {
    try {
      const hiveData = await hiveService.getById(id);
      setHive(hiveData);

      if (hiveData) {
        const colonyData = await hiveService.getActiveColony(hiveData.id);
        setColony(colonyData);

        const inspectionsData = await inspectionService.getByHiveId(hiveData.id, 5);
        setRecentInspections(inspectionsData);

        const tasksData = await taskService.getByHiveId(hiveData.id);
        setTasks(tasksData);
      }
    } catch (error) {
      console.error('Failed to load hive:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  useEffect(() => {
    loadData();
  }, [id]);

  const handleStartInspection = () => {
    router.push({
      pathname: '/inspection/create',
      params: { hiveId: id },
    });
  };

  const handleToggleTask = async (taskId: string, currentStatus: string) => {
    try {
      if (currentStatus === 'pending') {
        await taskService.complete(taskId);
      } else {
        await taskService.update(taskId, { status: 'pending' });
      }
      await loadData();
    } catch (error) {
      console.error('Failed to toggle task:', error);
    }
  };

  if (!hive) {
    return (
      <View style={styles.loadingContainer}>
        <Text>Loading...</Text>
      </View>
    );
  }

  const lastInspection = recentInspections[0];

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      <View style={styles.header}>
        <View style={styles.headerTop}>
          <Text style={styles.hiveCode}>{hive.hive_code}</Text>
          <View style={[styles.statusBadge, { backgroundColor: getStatusColor(hive.status) }]}>
            <Text style={styles.statusText}>{hive.status.toUpperCase()}</Text>
          </View>
        </View>
        {hive.hive_type && <Text style={styles.hiveType}>{hive.hive_type}</Text>}
        {colony && (
          <View style={styles.colonyInfo}>
            <Text style={styles.colonyText}>
              👑 Queen: {colony.queen_year || 'Unknown'} ({colony.queen_origin || 'Unknown origin'})
            </Text>
            {colony.temperament_notes && (
              <Text style={styles.colonyText}>😊 {colony.temperament_notes}</Text>
            )}
          </View>
        )}
      </View>

      <View style={styles.quickActions}>
        <TouchableOpacity style={styles.primaryButton} onPress={handleStartInspection}>
          <Text style={styles.primaryButtonText}>🔍 Start Inspection</Text>
        </TouchableOpacity>
      </View>

      {lastInspection && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Last Inspection</Text>
          <TouchableOpacity
            style={styles.inspectionCard}
            onPress={() => router.push(`/inspection/${lastInspection.id}`)}
          >
            <Text style={styles.inspectionDate}>
              {format(new Date(lastInspection.datetime), 'MMM d, yyyy h:mm a')}
            </Text>
            <Text style={styles.inspectionTime}>
              {formatDistanceToNow(new Date(lastInspection.datetime), { addSuffix: true })}
            </Text>
            {lastInspection.freeform_notes && (
              <Text style={styles.inspectionNotes} numberOfLines={2}>
                {lastInspection.freeform_notes}
              </Text>
            )}
          </TouchableOpacity>
        </View>
      )}

      {tasks.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Tasks ({tasks.length})</Text>
          {tasks.map((task) => (
            <TouchableOpacity
              key={task.id}
              style={styles.taskCard}
              onPress={() => handleToggleTask(task.id, task.status)}
            >
              <View style={styles.taskHeader}>
                <View style={styles.checkbox}>
                  {task.status === 'completed' && <Text style={styles.checkmark}>✓</Text>}
                </View>
                <View style={styles.taskContent}>
                  <Text
                    style={[
                      styles.taskTitle,
                      task.status === 'completed' && styles.taskCompleted,
                    ]}
                  >
                    {task.title}
                  </Text>
                  {task.due_date && (
                    <Text style={styles.taskDue}>
                      Due: {format(new Date(task.due_date), 'MMM d')}
                    </Text>
                  )}
                </View>
                <View style={[styles.priorityBadge, { backgroundColor: getPriorityColor(task.priority) }]}>
                  <Text style={styles.priorityText}>{task.priority[0].toUpperCase()}</Text>
                </View>
              </View>
            </TouchableOpacity>
          ))}
        </View>
      )}

      {recentInspections.length > 1 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Recent Inspections</Text>
          {recentInspections.slice(1).map((inspection) => (
            <TouchableOpacity
              key={inspection.id}
              style={styles.historyCard}
              onPress={() => router.push(`/inspection/${inspection.id}`)}
            >
              <Text style={styles.historyDate}>
                {format(new Date(inspection.datetime), 'MMM d, yyyy')}
              </Text>
              {inspection.freeform_notes && (
                <Text style={styles.historyNotes} numberOfLines={1}>
                  {inspection.freeform_notes}
                </Text>
              )}
            </TouchableOpacity>
          ))}
        </View>
      )}
    </ScrollView>
  );
}

function getStatusColor(status: string): string {
  switch (status) {
    case 'active':
      return '#4CAF50';
    case 'inactive':
      return '#FFA500';
    case 'dead':
      return '#F44336';
    default:
      return '#999';
  }
}

function getPriorityColor(priority: string): string {
  switch (priority) {
    case 'high':
      return '#F44336';
    case 'medium':
      return '#FFA500';
    case 'low':
      return '#4CAF50';
    default:
      return '#999';
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  header: {
    backgroundColor: '#fff',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  headerTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  hiveCode: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  statusText: {
    color: '#fff',
    fontSize: 11,
    fontWeight: '600',
  },
  hiveType: {
    fontSize: 16,
    color: '#666',
    marginBottom: 8,
  },
  colonyInfo: {
    marginTop: 8,
    gap: 4,
  },
  colonyText: {
    fontSize: 14,
    color: '#666',
  },
  quickActions: {
    padding: 16,
    backgroundColor: '#fff',
    marginTop: 8,
  },
  primaryButton: {
    backgroundColor: '#FFA500',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  primaryButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  section: {
    marginTop: 8,
    backgroundColor: '#fff',
    padding: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  inspectionCard: {
    padding: 12,
    backgroundColor: '#f9f9f9',
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#FFA500',
  },
  inspectionDate: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  inspectionTime: {
    fontSize: 12,
    color: '#999',
    marginTop: 2,
  },
  inspectionNotes: {
    fontSize: 14,
    color: '#666',
    marginTop: 8,
  },
  taskCard: {
    marginBottom: 8,
    padding: 12,
    backgroundColor: '#f9f9f9',
    borderRadius: 8,
  },
  taskHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  checkbox: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#FFA500',
    justifyContent: 'center',
    alignItems: 'center',
  },
  checkmark: {
    color: '#FFA500',
    fontSize: 16,
    fontWeight: 'bold',
  },
  taskContent: {
    flex: 1,
  },
  taskTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  taskCompleted: {
    textDecorationLine: 'line-through',
    color: '#999',
  },
  taskDue: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  priorityBadge: {
    width: 28,
    height: 28,
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
  },
  priorityText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  historyCard: {
    padding: 12,
    backgroundColor: '#f9f9f9',
    borderRadius: 8,
    marginBottom: 8,
  },
  historyDate: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  historyNotes: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
});
