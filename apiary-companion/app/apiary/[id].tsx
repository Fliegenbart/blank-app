import { useEffect, useState } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  RefreshControl,
} from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { apiaryService } from '../../src/services/apiaryService';
import { hiveService } from '../../src/services/hiveService';
import { Apiary, Hive } from '../../src/types';
import { format } from 'date-fns';

export default function ApiaryDetailScreen() {
  const router = useRouter();
  const { id } = useLocalSearchParams<{ id: string }>();
  const [apiary, setApiary] = useState<Apiary | null>(null);
  const [hives, setHives] = useState<Hive[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [hiveStats, setHiveStats] = useState<Record<string, { lastInspection: string | null; tasks: number }>>({});

  const loadData = async () => {
    try {
      const apiaryData = await apiaryService.getById(id);
      setApiary(apiaryData);

      if (apiaryData) {
        const hivesData = await hiveService.getByApiaryId(apiaryData.id);
        setHives(hivesData);

        // Load stats for each hive
        const stats: Record<string, { lastInspection: string | null; tasks: number }> = {};
        for (const hive of hivesData) {
          const lastInspection = await hiveService.getLastInspectionDate(hive.id);
          const tasksCount = await hiveService.getOpenTasksCount(hive.id);
          stats[hive.id] = { lastInspection, tasks: tasksCount };
        }
        setHiveStats(stats);
      }
    } catch (error) {
      console.error('Failed to load apiary:', error);
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

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return '#4CAF50';
      case 'inactive':
        return '#FFA500';
      case 'dead':
        return '#F44336';
      case 'sold':
        return '#9E9E9E';
      default:
        return '#999';
    }
  };

  const renderHiveCard = ({ item }: { item: Hive }) => {
    const stats = hiveStats[item.id];
    const lastInspectionText = stats?.lastInspection
      ? format(new Date(stats.lastInspection), 'MMM d, yyyy')
      : 'Never inspected';

    return (
      <TouchableOpacity
        style={styles.card}
        onPress={() => router.push(`/hive/${item.id}`)}
      >
        <View style={styles.cardHeader}>
          <View style={styles.hiveCodeContainer}>
            <Text style={styles.hiveCode}>{item.hive_code}</Text>
            <View style={[styles.statusDot, { backgroundColor: getStatusColor(item.status) }]} />
          </View>
          {stats?.tasks > 0 && (
            <View style={styles.taskBadge}>
              <Text style={styles.taskBadgeText}>{stats.tasks} tasks</Text>
            </View>
          )}
        </View>

        {item.hive_type && (
          <Text style={styles.hiveType}>{item.hive_type}</Text>
        )}

        <View style={styles.statsRow}>
          <Text style={styles.statText}>📅 Last: {lastInspectionText}</Text>
        </View>

        {item.notes && (
          <Text style={styles.notes} numberOfLines={2}>
            {item.notes}
          </Text>
        )}
      </TouchableOpacity>
    );
  };

  if (!apiary) {
    return (
      <View style={styles.loadingContainer}>
        <Text>Loading...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.apiaryName}>{apiary.name}</Text>
        {apiary.location_approx && (
          <Text style={styles.location}>📍 {apiary.location_approx}</Text>
        )}
      </View>

      <FlatList
        data={hives}
        renderItem={renderHiveCard}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>No hives in this apiary</Text>
          </View>
        }
      />
    </View>
  );
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
  apiaryName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  location: {
    fontSize: 14,
    color: '#666',
  },
  list: {
    padding: 16,
  },
  card: {
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
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  hiveCodeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  hiveCode: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  statusDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
  },
  taskBadge: {
    backgroundColor: '#FF5722',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  taskBadgeText: {
    color: '#fff',
    fontSize: 11,
    fontWeight: '600',
  },
  hiveType: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  statsRow: {
    flexDirection: 'row',
    gap: 16,
    marginTop: 8,
  },
  statText: {
    fontSize: 12,
    color: '#666',
  },
  notes: {
    fontSize: 12,
    color: '#999',
    marginTop: 8,
    fontStyle: 'italic',
  },
  emptyContainer: {
    alignItems: 'center',
    marginTop: 60,
  },
  emptyText: {
    fontSize: 16,
    color: '#999',
  },
});
