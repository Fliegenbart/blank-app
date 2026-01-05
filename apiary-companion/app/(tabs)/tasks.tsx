import { useEffect, useState } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  RefreshControl,
} from 'react-native';
import { useRouter } from 'expo-router';
import { taskService } from '../../src/services/taskService';
import { hiveService } from '../../src/services/hiveService';
import { Task } from '../../src/types';
import { format, isPast } from 'date-fns';

type Filter = 'all' | 'overdue' | 'pending';

export default function TasksTab() {
  const router = useRouter();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [filter, setFilter] = useState<Filter>('pending');
  const [hiveNames, setHiveNames] = useState<Record<string, string>>({});

  const loadTasks = async () => {
    try {
      let data: Task[];
      if (filter === 'overdue') {
        data = await taskService.getOverdue();
      } else if (filter === 'all') {
        data = await taskService.getAllPending();
      } else {
        data = await taskService.getAllPending();
      }

      setTasks(data);

      // Load hive names
      const names: Record<string, string> = {};
      for (const task of data) {
        if (task.hive_id && !names[task.hive_id]) {
          const hive = await hiveService.getById(task.hive_id);
          if (hive) {
            names[task.hive_id] = hive.hive_code;
          }
        }
      }
      setHiveNames(names);
    } catch (error) {
      console.error('Failed to load tasks:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadTasks();
    setRefreshing(false);
  };

  useEffect(() => {
    loadTasks();
  }, [filter]);

  const handleToggleTask = async (taskId: string, currentStatus: string) => {
    try {
      if (currentStatus === 'pending') {
        await taskService.complete(taskId);
      } else {
        await taskService.update(taskId, { status: 'pending' });
      }
      await loadTasks();
    } catch (error) {
      console.error('Failed to toggle task:', error);
    }
  };

  const isOverdue = (task: Task): boolean => {
    if (!task.due_date) return false;
    return task.status === 'pending' && isPast(new Date(task.due_date));
  };

  const renderTask = ({ item }: { item: Task }) => {
    const overdue = isOverdue(item);

    return (
      <TouchableOpacity
        style={[styles.taskCard, overdue && styles.taskCardOverdue]}
        onPress={() => handleToggleTask(item.id, item.status)}
      >
        <View style={styles.taskHeader}>
          <View style={styles.checkbox}>
            {item.status === 'completed' && <Text style={styles.checkmark}>✓</Text>}
          </View>

          <View style={styles.taskContent}>
            <Text
              style={[
                styles.taskTitle,
                item.status === 'completed' && styles.taskCompleted,
              ]}
            >
              {item.title}
            </Text>

            {item.hive_id && hiveNames[item.hive_id] && (
              <Text style={styles.taskHive}>🐝 {hiveNames[item.hive_id]}</Text>
            )}

            {item.description && (
              <Text style={styles.taskDescription} numberOfLines={2}>
                {item.description}
              </Text>
            )}

            {item.due_date && (
              <Text style={[styles.taskDue, overdue && styles.taskDueOverdue]}>
                {overdue ? '⚠️ Overdue: ' : 'Due: '}
                {format(new Date(item.due_date), 'MMM d, yyyy')}
              </Text>
            )}

            <Text style={styles.taskSource}>
              {item.source === 'inspection_suggestion' && '🔍 From inspection'}
              {item.source === 'seasonal_plan' && '📅 Seasonal'}
              {item.source === 'manual' && '✍️ Manual'}
            </Text>
          </View>

          <View style={[styles.priorityBadge, { backgroundColor: getPriorityColor(item.priority) }]}>
            <Text style={styles.priorityText}>{item.priority[0].toUpperCase()}</Text>
          </View>
        </View>
      </TouchableOpacity>
    );
  };

  const pendingTasks = tasks.filter(t => t.status === 'pending');
  const overdueTasks = pendingTasks.filter(isOverdue);

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Tasks</Text>
        <View style={styles.stats}>
          <Text style={styles.statsText}>
            {pendingTasks.length} pending
            {overdueTasks.length > 0 && ` • ${overdueTasks.length} overdue`}
          </Text>
        </View>
      </View>

      <View style={styles.filters}>
        <TouchableOpacity
          style={[styles.filterButton, filter === 'pending' && styles.filterButtonActive]}
          onPress={() => setFilter('pending')}
        >
          <Text style={[styles.filterText, filter === 'pending' && styles.filterTextActive]}>
            Pending
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.filterButton, filter === 'overdue' && styles.filterButtonActive]}
          onPress={() => setFilter('overdue')}
        >
          <Text style={[styles.filterText, filter === 'overdue' && styles.filterTextActive]}>
            Overdue
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.filterButton, filter === 'all' && styles.filterButtonActive]}
          onPress={() => setFilter('all')}
        >
          <Text style={[styles.filterText, filter === 'all' && styles.filterTextActive]}>
            All
          </Text>
        </TouchableOpacity>
      </View>

      <FlatList
        data={tasks}
        renderItem={renderTask}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>No tasks to show</Text>
            <Text style={styles.emptySubtext}>
              Tasks will appear here from inspections and seasonal plans
            </Text>
          </View>
        }
      />
    </View>
  );
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
  header: {
    backgroundColor: '#FFA500',
    padding: 16,
    paddingTop: 60,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
  },
  stats: {
    marginTop: 4,
  },
  statsText: {
    fontSize: 14,
    color: '#fff',
    opacity: 0.9,
  },
  filters: {
    flexDirection: 'row',
    padding: 16,
    gap: 8,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  filterButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#DDD',
    backgroundColor: '#fff',
  },
  filterButtonActive: {
    borderColor: '#FFA500',
    backgroundColor: '#FFA500',
  },
  filterText: {
    fontSize: 14,
    color: '#666',
    fontWeight: '600',
  },
  filterTextActive: {
    color: '#fff',
  },
  list: {
    padding: 16,
  },
  taskCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  taskCardOverdue: {
    borderLeftWidth: 4,
    borderLeftColor: '#F44336',
  },
  taskHeader: {
    flexDirection: 'row',
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
    marginTop: 2,
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
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  taskCompleted: {
    textDecorationLine: 'line-through',
    color: '#999',
  },
  taskHive: {
    fontSize: 12,
    color: '#FFA500',
    marginBottom: 4,
    fontWeight: '600',
  },
  taskDescription: {
    fontSize: 13,
    color: '#666',
    marginBottom: 6,
  },
  taskDue: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  taskDueOverdue: {
    color: '#F44336',
    fontWeight: '600',
  },
  taskSource: {
    fontSize: 11,
    color: '#999',
    fontStyle: 'italic',
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
  emptyContainer: {
    alignItems: 'center',
    marginTop: 100,
  },
  emptyText: {
    fontSize: 18,
    color: '#999',
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#bbb',
    textAlign: 'center',
  },
});
