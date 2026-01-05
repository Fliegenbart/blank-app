import { useEffect, useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
} from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { inspectionService } from '../../src/services/inspectionService';
import { hiveService } from '../../src/services/hiveService';
import { Inspection, InspectionFindings, Hive } from '../../src/types';
import { format } from 'date-fns';

export default function InspectionDetailScreen() {
  const router = useRouter();
  const { id } = useLocalSearchParams<{ id: string }>();
  const [inspection, setInspection] = useState<Inspection | null>(null);
  const [findings, setFindings] = useState<InspectionFindings | null>(null);
  const [hive, setHive] = useState<Hive | null>(null);

  useEffect(() => {
    loadInspection();
  }, [id]);

  const loadInspection = async () => {
    try {
      const inspectionData = await inspectionService.getById(id);
      if (!inspectionData) return;

      setInspection(inspectionData);

      const findingsData = await inspectionService.getFindings(inspectionData.id);
      setFindings(findingsData);

      const hiveData = await hiveService.getById(inspectionData.hive_id);
      setHive(hiveData);
    } catch (error) {
      console.error('Failed to load inspection:', error);
    }
  };

  if (!inspection) {
    return (
      <View style={styles.loadingContainer}>
        <Text>Loading...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.date}>
          {format(new Date(inspection.datetime), 'MMMM d, yyyy')}
        </Text>
        <Text style={styles.time}>
          {format(new Date(inspection.datetime), 'h:mm a')}
        </Text>
        {hive && <Text style={styles.hive}>Hive: {hive.hive_code}</Text>}
      </View>

      {(inspection.weather || inspection.inspector) && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Conditions</Text>
          {inspection.weather && (
            <View style={styles.row}>
              <Text style={styles.label}>Weather:</Text>
              <Text style={styles.value}>{inspection.weather}</Text>
            </View>
          )}
          {inspection.inspector && (
            <View style={styles.row}>
              <Text style={styles.label}>Inspector:</Text>
              <Text style={styles.value}>{inspection.inspector}</Text>
            </View>
          )}
        </View>
      )}

      {findings && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Findings</Text>

          {findings.queen_seen !== null && (
            <View style={styles.row}>
              <Text style={styles.label}>Queen Seen:</Text>
              <Text style={styles.value}>{findings.queen_seen ? 'Yes ✓' : 'No'}</Text>
            </View>
          )}

          {findings.eggs_seen !== null && (
            <View style={styles.row}>
              <Text style={styles.label}>Eggs Seen:</Text>
              <Text style={styles.value}>{findings.eggs_seen ? 'Yes ✓' : 'No'}</Text>
            </View>
          )}

          {findings.brood_pattern && (
            <View style={styles.row}>
              <Text style={styles.label}>Brood Pattern:</Text>
              <Text style={styles.value}>{findings.brood_pattern}</Text>
            </View>
          )}

          {findings.population_strength && (
            <View style={styles.row}>
              <Text style={styles.label}>Population:</Text>
              <Text style={styles.value}>{findings.population_strength}/10</Text>
            </View>
          )}

          {findings.temperament && (
            <View style={styles.row}>
              <Text style={styles.label}>Temperament:</Text>
              <Text style={styles.value}>{findings.temperament}</Text>
            </View>
          )}

          {findings.swarm_signs !== null && (
            <View style={styles.row}>
              <Text style={styles.label}>Swarm Signs:</Text>
              <Text style={[styles.value, findings.swarm_signs && styles.warning]}>
                {findings.swarm_signs ? '⚠️ Yes' : 'No'}
              </Text>
            </View>
          )}

          {findings.swarm_signs_detail && (
            <View style={styles.row}>
              <Text style={styles.label}>Details:</Text>
              <Text style={styles.value}>{findings.swarm_signs_detail}</Text>
            </View>
          )}

          {findings.stores_honey && (
            <View style={styles.row}>
              <Text style={styles.label}>Honey Stores:</Text>
              <Text style={styles.value}>{findings.stores_honey}/10</Text>
            </View>
          )}

          {findings.stores_pollen && (
            <View style={styles.row}>
              <Text style={styles.label}>Pollen Stores:</Text>
              <Text style={styles.value}>{findings.stores_pollen}/10</Text>
            </View>
          )}

          {findings.pests_observed && (
            <View style={styles.row}>
              <Text style={styles.label}>Pests:</Text>
              <Text style={styles.value}>{findings.pests_observed}</Text>
            </View>
          )}

          {findings.varroa_count_value !== null && (
            <View style={styles.row}>
              <Text style={styles.label}>Varroa Count:</Text>
              <Text style={styles.value}>
                {findings.varroa_count_value}
                {findings.varroa_count_method && ` (${findings.varroa_count_method})`}
              </Text>
            </View>
          )}

          {findings.disease_flags && (
            <View style={[styles.row, styles.warningRow]}>
              <Text style={styles.label}>⚠️ Disease Flags:</Text>
              <Text style={styles.warning}>{findings.disease_flags}</Text>
            </View>
          )}

          {findings.equipment_changes && (
            <View style={styles.row}>
              <Text style={styles.label}>Equipment:</Text>
              <Text style={styles.value}>{findings.equipment_changes}</Text>
            </View>
          )}
        </View>
      )}

      {inspection.freeform_notes && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Notes</Text>
          <Text style={styles.notes}>{inspection.freeform_notes}</Text>
        </View>
      )}

      {inspection.voice_transcript && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Voice Transcript</Text>
          <Text style={styles.notes}>{inspection.voice_transcript}</Text>
        </View>
      )}

      {inspection.is_structured && (
        <View style={styles.badge}>
          <Text style={styles.badgeText}>✓ AI Structured</Text>
        </View>
      )}
    </ScrollView>
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
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  date: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  time: {
    fontSize: 16,
    color: '#666',
    marginTop: 4,
  },
  hive: {
    fontSize: 14,
    color: '#FFA500',
    marginTop: 8,
    fontWeight: '600',
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
    marginBottom: 12,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  label: {
    fontSize: 14,
    color: '#666',
    fontWeight: '500',
    flex: 1,
  },
  value: {
    fontSize: 14,
    color: '#333',
    fontWeight: '600',
    flex: 1,
    textAlign: 'right',
  },
  warning: {
    color: '#F44336',
  },
  warningRow: {
    backgroundColor: '#FFF3E0',
    marginHorizontal: -16,
    paddingHorizontal: 16,
  },
  notes: {
    fontSize: 14,
    color: '#333',
    lineHeight: 22,
  },
  badge: {
    backgroundColor: '#4CAF50',
    padding: 12,
    marginTop: 8,
    alignItems: 'center',
  },
  badgeText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
});
