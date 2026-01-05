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
import { apiaryService } from '../src/services/apiaryService';
import { hiveService } from '../src/services/hiveService';
import { userService } from '../src/services/userService';
import { Apiary } from '../src/types';

export default function ApiariesScreen() {
  const router = useRouter();
  const [apiaries, setApiaries] = useState<Apiary[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [hiveCounts, setHiveCounts] = useState<Record<string, number>>({});

  const loadApiaries = async () => {
    try {
      const user = await userService.getCurrentUser();
      if (!user) return;

      const data = await apiaryService.getByUserId(user.id);
      setApiaries(data);

      // Load hive counts for each apiary
      const counts: Record<string, number> = {};
      for (const apiary of data) {
        const hives = await hiveService.getByApiaryId(apiary.id);
        counts[apiary.id] = hives.filter(h => h.status === 'active').length;
      }
      setHiveCounts(counts);
    } catch (error) {
      console.error('Failed to load apiaries:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadApiaries();
    setRefreshing(false);
  };

  useEffect(() => {
    loadApiaries();
  }, []);

  const renderApiaryCard = ({ item }: { item: Apiary }) => (
    <TouchableOpacity
      style={styles.card}
      onPress={() => router.push(`/apiary/${item.id}`)}
    >
      <View style={styles.cardHeader}>
        <Text style={styles.cardTitle}>{item.name}</Text>
        <View style={styles.badge}>
          <Text style={styles.badgeText}>{hiveCounts[item.id] || 0} hives</Text>
        </View>
      </View>
      {item.location_approx && (
        <Text style={styles.cardSubtitle}>📍 {item.location_approx}</Text>
      )}
      <Text style={styles.cardSubtitle}>🌍 {item.timezone}</Text>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <FlatList
        data={apiaries}
        renderItem={renderApiaryCard}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>No apiaries yet</Text>
            <Text style={styles.emptySubtext}>Pull to refresh or add your first apiary</Text>
          </View>
        }
      />

      <TouchableOpacity
        style={styles.fab}
        onPress={() => router.push('/(tabs)/apiaries')}
      >
        <Text style={styles.fabText}>📋 View All</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
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
  cardTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    flex: 1,
  },
  cardSubtitle: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  badge: {
    backgroundColor: '#FFA500',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  badgeText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
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
  },
  fab: {
    position: 'absolute',
    right: 20,
    bottom: 20,
    backgroundColor: '#FFA500',
    paddingHorizontal: 24,
    paddingVertical: 16,
    borderRadius: 30,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 8,
  },
  fabText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
