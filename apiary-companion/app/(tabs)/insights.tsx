import { useEffect, useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  RefreshControl,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { userService } from '../../src/services/userService';
import { apiaryService } from '../../src/services/apiaryService';
import { hiveService } from '../../src/services/hiveService';
import { inspectionService } from '../../src/services/inspectionService';
import { taskService } from '../../src/services/taskService';
import * as Sharing from 'expo-sharing';
import * as FileSystem from 'expo-file-system';
import { format } from 'date-fns';

export default function InsightsTab() {
  const [refreshing, setRefreshing] = useState(false);
  const [stats, setStats] = useState({
    totalApiaries: 0,
    totalHives: 0,
    activeHives: 0,
    totalInspections: 0,
    pendingTasks: 0,
  });

  const loadStats = async () => {
    try {
      const user = await userService.getCurrentUser();
      if (!user) return;

      const apiaries = await apiaryService.getByUserId(user.id);
      let hiveCount = 0;
      let activeCount = 0;
      let inspectionCount = 0;

      for (const apiary of apiaries) {
        const hives = await hiveService.getByApiaryId(apiary.id);
        hiveCount += hives.length;
        activeCount += hives.filter(h => h.status === 'active').length;

        for (const hive of hives) {
          const inspections = await inspectionService.getByHiveId(hive.id);
          inspectionCount += inspections.length;
        }
      }

      const tasks = await taskService.getAllPending();

      setStats({
        totalApiaries: apiaries.length,
        totalHives: hiveCount,
        activeHives: activeCount,
        totalInspections: inspectionCount,
        pendingTasks: tasks.length,
      });
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadStats();
    setRefreshing(false);
  };

  useEffect(() => {
    loadStats();
  }, []);

  const handleExportData = async () => {
    try {
      const user = await userService.getCurrentUser();
      if (!user) return;

      const apiaries = await apiaryService.getByUserId(user.id);
      const exportData: any[] = [];

      for (const apiary of apiaries) {
        const hives = await hiveService.getByApiaryId(apiary.id);

        for (const hive of hives) {
          const inspections = await inspectionService.getByHiveId(hive.id);

          for (const inspection of inspections) {
            const findings = await inspectionService.getFindings(inspection.id);

            exportData.push({
              Apiary: apiary.name,
              Hive: hive.hive_code,
              Date: format(new Date(inspection.datetime), 'yyyy-MM-dd HH:mm'),
              Weather: inspection.weather || '',
              Inspector: inspection.inspector || '',
              Notes: inspection.freeform_notes || '',
              QueenSeen: findings?.queen_seen ? 'Yes' : 'No',
              EggsSeen: findings?.eggs_seen ? 'Yes' : 'No',
              SwarmSigns: findings?.swarm_signs ? 'Yes' : 'No',
              PopulationStrength: findings?.population_strength || '',
              Temperament: findings?.temperament || '',
              VarroaCount: findings?.varroa_count_value || '',
            });
          }
        }
      }

      // Convert to CSV
      if (exportData.length === 0) {
        Alert.alert('No Data', 'No inspection data to export');
        return;
      }

      const headers = Object.keys(exportData[0]).join(',');
      const rows = exportData.map(row =>
        Object.values(row).map(val =>
          typeof val === 'string' && val.includes(',') ? `"${val}"` : val
        ).join(',')
      );
      const csv = [headers, ...rows].join('\n');

      // Save to file
      const fileUri = FileSystem.documentDirectory + `apiary-export-${Date.now()}.csv`;
      await FileSystem.writeAsStringAsync(fileUri, csv, {
        encoding: FileSystem.EncodingType.UTF8,
      });

      // Share file
      if (await Sharing.isAvailableAsync()) {
        await Sharing.shareAsync(fileUri, {
          mimeType: 'text/csv',
          dialogTitle: 'Export Apiary Data',
        });
      } else {
        Alert.alert('Success', `Data exported to ${fileUri}`);
      }
    } catch (error) {
      console.error('Export failed:', error);
      Alert.alert('Error', 'Failed to export data');
    }
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Insights</Text>
      </View>

      <View style={styles.statsGrid}>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>{stats.totalApiaries}</Text>
          <Text style={styles.statLabel}>Apiaries</Text>
        </View>

        <View style={styles.statCard}>
          <Text style={styles.statValue}>{stats.activeHives}</Text>
          <Text style={styles.statLabel}>Active Hives</Text>
        </View>

        <View style={styles.statCard}>
          <Text style={styles.statValue}>{stats.totalInspections}</Text>
          <Text style={styles.statLabel}>Total Inspections</Text>
        </View>

        <View style={styles.statCard}>
          <Text style={styles.statValue}>{stats.pendingTasks}</Text>
          <Text style={styles.statLabel}>Pending Tasks</Text>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Data Management</Text>

        <TouchableOpacity style={styles.exportButton} onPress={handleExportData}>
          <Text style={styles.exportButtonText}>📄 Export All Data (CSV)</Text>
        </TouchableOpacity>

        <View style={styles.infoBox}>
          <Text style={styles.infoTitle}>🔒 Privacy & GDPR</Text>
          <Text style={styles.infoText}>
            • All data stored locally on your device
            {'\n'}• Export your data anytime
            {'\n'}• No cloud sync without explicit consent
            {'\n'}• Full control over your beekeeping records
          </Text>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>About Apiary Companion</Text>
        <Text style={styles.aboutText}>
          Version 1.0.0 (MVP)
          {'\n\n'}
          Designed for hobby and semi-pro beekeepers in the EU.
          {'\n\n'}
          Built with offline-first architecture using React Native and SQLite.
        </Text>
      </View>
    </ScrollView>
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
    paddingBottom: 24,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 16,
    gap: 12,
  },
  statCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    flex: 1,
    minWidth: '45%',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statValue: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#FFA500',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
  },
  section: {
    backgroundColor: '#fff',
    padding: 16,
    marginTop: 8,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
  },
  exportButton: {
    backgroundColor: '#4CAF50',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 16,
  },
  exportButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  infoBox: {
    backgroundColor: '#E3F2FD',
    padding: 16,
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#2196F3',
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1976D2',
    marginBottom: 8,
  },
  infoText: {
    fontSize: 14,
    color: '#1565C0',
    lineHeight: 20,
  },
  aboutText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 22,
  },
});
