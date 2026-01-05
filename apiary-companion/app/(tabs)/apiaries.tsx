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
import { apiaryService } from '../../src/services/apiaryService';
import { hiveService } from '../../src/services/hiveService';
import { userService } from '../../src/services/userService';
import { Apiary, Hive } from '../../src/types';

export default function ApiariesTab() {
  const router = useRouter();
  const [apiaries, setApiaries] = useState<Apiary[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [hivesMap, setHivesMap] = useState<Record<string, Hive[]>>({});

  const loadApiaries = async () => {
    try {
      const user = await userService.getCurrentUser();
      if (!user) return;

      const data = await apiaryService.getByUserId(user.id);
      setApiaries(data);

      // Load hives for all apiaries
      const hives: Record<string, Hive[]> = {};
      for (const apiary of data) {
        const apiaryHives = await hiveService.getByApiaryId(apiary.id);
        hives[apiary.id] = apiaryHives;
      }
      setHivesMap(hives);
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

  const renderApiaryCard = ({ item }: { item: Apiary }) => {
    const isExpanded = expandedId === item.id;
    const hives = hivesMap[item.id] || [];
    const activeHives = hives.filter(h => h.status === 'active').length;

    return (
      <View style={styles.card}>
        <TouchableOpacity
          onPress={() => setExpandedId(isExpanded ? null : item.id)}
        >
          <View style={styles.cardHeader}>
            <Text style={styles.cardTitle}>{item.name}</Text>
            <View style={styles.badge}>
              <Text style={styles.badgeText}>{activeHives} hives</Text>
            </View>
          </View>
          {item.location_approx && (
            <Text style={styles.cardSubtitle}>📍 {item.location_approx}</Text>
          )}
        </TouchableOpacity>

        {isExpanded && (
          <View style={styles.hivesContainer}>
            {hives.map((hive) => (
              <TouchableOpacity
                key={hive.id}
                style={styles.hiveItem}
                onPress={() => router.push(`/hive/${hive.id}`)}
              >
                <Text style={styles.hiveCode}>{hive.hive_code}</Text>
                <Text style={styles.hiveStatus}>{hive.status}</Text>
              </TouchableOpacity>
            ))}
          </View>
        )}
      </View>
    );
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>My Apiaries</Text>
      </View>

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
  hivesContainer: {
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  hiveItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 10,
    paddingHorizontal: 12,
    backgroundColor: '#f9f9f9',
    borderRadius: 8,
    marginBottom: 6,
  },
  hiveCode: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  hiveStatus: {
    fontSize: 12,
    color: '#666',
    textTransform: 'capitalize',
  },
  emptyContainer: {
    alignItems: 'center',
    marginTop: 100,
  },
  emptyText: {
    fontSize: 18,
    color: '#999',
  },
});
