import { useEffect, useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { inspectionService } from '../../src/services/inspectionService';
import { taskService } from '../../src/services/taskService';
import { llmService } from '../../src/services/llmService';
import { Inspection, InspectionStructuredData } from '../../src/types';

export default function ReviewInspectionScreen() {
  const router = useRouter();
  const { inspectionId } = useLocalSearchParams<{ inspectionId: string }>();

  const [inspection, setInspection] = useState<Inspection | null>(null);
  const [structuredData, setStructuredData] = useState<InspectionStructuredData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadAndStructure();
  }, [inspectionId]);

  const loadAndStructure = async () => {
    try {
      const inspectionData = await inspectionService.getById(inspectionId);
      if (!inspectionData) {
        Alert.alert('Error', 'Inspection not found');
        router.back();
        return;
      }

      setInspection(inspectionData);

      // Run LLM structuring
      if (inspectionData.freeform_notes || inspectionData.voice_transcript) {
        const structured = await llmService.structureInspectionNotes(
          inspectionData.freeform_notes || '',
          inspectionData.voice_transcript || undefined
        );
        setStructuredData(structured);
      }

      setLoading(false);
    } catch (error) {
      console.error('Failed to load inspection:', error);
      Alert.alert('Error', 'Failed to load inspection');
      setLoading(false);
    }
  };

  const handleConfirm = async () => {
    if (!inspection || !structuredData) return;

    setSaving(true);

    try {
      // Update or create findings with structured data
      await inspectionService.updateFindings(inspection.id, structuredData.findings);

      // Mark inspection as structured
      await inspectionService.update(inspection.id, { is_structured: true });

      // Create suggested tasks
      if (structuredData.suggestedTasks.length > 0) {
        await taskService.createSuggestedTasks(inspection.hive_id, structuredData.suggestedTasks);
      }

      Alert.alert(
        'Success',
        `Inspection structured with ${structuredData.suggestedTasks.length} tasks created.`,
        [
          {
            text: 'OK',
            onPress: () => router.back(),
          },
        ]
      );
    } catch (error) {
      console.error('Failed to save structured data:', error);
      Alert.alert('Error', 'Failed to save structured data');
      setSaving(false);
    }
  };

  const handleSkip = async () => {
    if (!inspection) return;

    try {
      await inspectionService.update(inspection.id, { is_structured: true });
      router.back();
    } catch (error) {
      console.error('Failed to update inspection:', error);
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#FFA500" />
        <Text style={styles.loadingText}>Analyzing inspection notes...</Text>
        <Text style={styles.loadingSubtext}>
          Using AI to extract structured findings
        </Text>
      </View>
    );
  }

  if (!structuredData) {
    return (
      <View style={styles.container}>
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyText}>No data to structure</Text>
          <TouchableOpacity style={styles.button} onPress={() => router.back()}>
            <Text style={styles.buttonText}>Go Back</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  const { findings, suggestedTasks, confidence } = structuredData;

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Review Extracted Data</Text>
        <View style={styles.confidenceBadge}>
          <Text style={styles.confidenceText}>
            Confidence: {Math.round(confidence * 100)}%
          </Text>
        </View>
        <Text style={styles.subtitle}>
          Please review and confirm the information extracted from your notes
        </Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🔍 Findings Detected</Text>

        {findings.queen_seen !== null && findings.queen_seen !== undefined && (
          <View style={styles.findingRow}>
            <Text style={styles.findingLabel}>Queen Seen:</Text>
            <Text style={styles.findingValue}>{findings.queen_seen ? 'Yes ✓' : 'No'}</Text>
          </View>
        )}

        {findings.eggs_seen !== null && findings.eggs_seen !== undefined && (
          <View style={styles.findingRow}>
            <Text style={styles.findingLabel}>Eggs Seen:</Text>
            <Text style={styles.findingValue}>{findings.eggs_seen ? 'Yes ✓' : 'No'}</Text>
          </View>
        )}

        {findings.brood_pattern && (
          <View style={styles.findingRow}>
            <Text style={styles.findingLabel}>Brood Pattern:</Text>
            <Text style={styles.findingValue}>{findings.brood_pattern}</Text>
          </View>
        )}

        {findings.population_strength && (
          <View style={styles.findingRow}>
            <Text style={styles.findingLabel}>Population Strength:</Text>
            <Text style={styles.findingValue}>{findings.population_strength}/10</Text>
          </View>
        )}

        {findings.temperament && (
          <View style={styles.findingRow}>
            <Text style={styles.findingLabel}>Temperament:</Text>
            <Text style={styles.findingValue}>{findings.temperament}</Text>
          </View>
        )}

        {findings.swarm_signs !== null && findings.swarm_signs !== undefined && (
          <View style={styles.findingRow}>
            <Text style={styles.findingLabel}>Swarm Signs:</Text>
            <Text style={[styles.findingValue, findings.swarm_signs && styles.warningText]}>
              {findings.swarm_signs ? '⚠️ Yes' : 'No'}
            </Text>
          </View>
        )}

        {findings.swarm_signs_detail && (
          <View style={styles.findingRow}>
            <Text style={styles.findingLabel}>Details:</Text>
            <Text style={styles.findingValue}>{findings.swarm_signs_detail}</Text>
          </View>
        )}

        {findings.stores_honey && (
          <View style={styles.findingRow}>
            <Text style={styles.findingLabel}>Honey Stores:</Text>
            <Text style={styles.findingValue}>{findings.stores_honey}/10</Text>
          </View>
        )}

        {findings.stores_pollen && (
          <View style={styles.findingRow}>
            <Text style={styles.findingLabel}>Pollen Stores:</Text>
            <Text style={styles.findingValue}>{findings.stores_pollen}/10</Text>
          </View>
        )}

        {findings.pests_observed && (
          <View style={styles.findingRow}>
            <Text style={styles.findingLabel}>Pests Observed:</Text>
            <Text style={styles.findingValue}>{findings.pests_observed}</Text>
          </View>
        )}

        {findings.varroa_count_value !== null && findings.varroa_count_value !== undefined && (
          <View style={styles.findingRow}>
            <Text style={styles.findingLabel}>Varroa Count:</Text>
            <Text style={styles.findingValue}>
              {findings.varroa_count_value}
              {findings.varroa_count_method && ` (${findings.varroa_count_method})`}
            </Text>
          </View>
        )}

        {findings.disease_flags && (
          <View style={[styles.findingRow, styles.warningRow]}>
            <Text style={styles.findingLabel}>⚠️ Disease Flags:</Text>
            <Text style={styles.warningText}>{findings.disease_flags}</Text>
          </View>
        )}

        {findings.equipment_changes && (
          <View style={styles.findingRow}>
            <Text style={styles.findingLabel}>Equipment Changes:</Text>
            <Text style={styles.findingValue}>{findings.equipment_changes}</Text>
          </View>
        )}
      </View>

      {suggestedTasks.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>📋 Suggested Tasks ({suggestedTasks.length})</Text>
          <Text style={styles.tasksHint}>
            These tasks will be created based on your inspection findings
          </Text>

          {suggestedTasks.map((task, index) => (
            <View key={index} style={styles.taskCard}>
              <View style={styles.taskHeader}>
                <Text style={styles.taskTitle}>{task.title}</Text>
                <View style={[styles.priorityBadge, { backgroundColor: getPriorityColor(task.priority) }]}>
                  <Text style={styles.priorityText}>{task.priority.toUpperCase()}</Text>
                </View>
              </View>
              <Text style={styles.taskDescription}>{task.description}</Text>
              <Text style={styles.taskDue}>
                Due in {task.dueInDays} day{task.dueInDays !== 1 ? 's' : ''}
              </Text>
            </View>
          ))}
        </View>
      )}

      <View style={styles.disclaimer}>
        <Text style={styles.disclaimerText}>
          ⚠️ This is AI-assisted analysis. Please verify all information and consult local beekeeping experts for disease diagnosis or treatment advice.
        </Text>
      </View>

      <View style={styles.bottomButtons}>
        <TouchableOpacity
          style={[styles.confirmButton, saving && styles.buttonDisabled]}
          onPress={handleConfirm}
          disabled={saving}
        >
          <Text style={styles.confirmButtonText}>
            {saving ? 'Saving...' : '✓ Confirm & Save'}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.skipButton}
          onPress={handleSkip}
          disabled={saving}
        >
          <Text style={styles.skipButtonText}>Skip Structuring</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
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
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  loadingText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginTop: 16,
  },
  loadingSubtext: {
    fontSize: 14,
    color: '#666',
    marginTop: 8,
    textAlign: 'center',
  },
  header: {
    backgroundColor: '#fff',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  title: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  confidenceBadge: {
    alignSelf: 'flex-start',
    backgroundColor: '#FFA500',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
    marginBottom: 8,
  },
  confidenceText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
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
  findingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  findingLabel: {
    fontSize: 14,
    color: '#666',
    fontWeight: '500',
    flex: 1,
  },
  findingValue: {
    fontSize: 14,
    color: '#333',
    fontWeight: '600',
    flex: 1,
    textAlign: 'right',
  },
  warningRow: {
    backgroundColor: '#FFF3E0',
    marginHorizontal: -16,
    paddingHorizontal: 16,
  },
  warningText: {
    color: '#F44336',
  },
  tasksHint: {
    fontSize: 12,
    color: '#999',
    marginBottom: 12,
  },
  taskCard: {
    backgroundColor: '#f9f9f9',
    padding: 12,
    borderRadius: 8,
    marginBottom: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#FFA500',
  },
  taskHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  taskTitle: {
    fontSize: 15,
    fontWeight: '600',
    color: '#333',
    flex: 1,
  },
  priorityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  priorityText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  taskDescription: {
    fontSize: 13,
    color: '#666',
    marginBottom: 6,
  },
  taskDue: {
    fontSize: 11,
    color: '#999',
    fontStyle: 'italic',
  },
  disclaimer: {
    backgroundColor: '#FFF3E0',
    padding: 16,
    marginTop: 8,
  },
  disclaimerText: {
    fontSize: 12,
    color: '#E65100',
    lineHeight: 18,
  },
  bottomButtons: {
    padding: 16,
    paddingBottom: 32,
  },
  confirmButton: {
    backgroundColor: '#4CAF50',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 12,
  },
  confirmButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  skipButton: {
    backgroundColor: '#f0f0f0',
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
  },
  skipButtonText: {
    color: '#666',
    fontSize: 16,
    fontWeight: '600',
  },
  buttonDisabled: {
    backgroundColor: '#CCC',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  emptyText: {
    fontSize: 18,
    color: '#999',
    marginBottom: 16,
  },
  button: {
    backgroundColor: '#FFA500',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});
