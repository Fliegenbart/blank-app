import { useState, useRef } from 'react';
import {
  View,
  Text,
  TextInput,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Alert,
  Platform,
} from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { CameraView, useCameraPermissions } from 'expo-camera';
import { Audio } from 'expo-av';
import * as FileSystem from 'expo-file-system';
import { inspectionService } from '../../src/services/inspectionService';
import { llmService } from '../../src/services/llmService';

export default function CreateInspectionScreen() {
  const router = useRouter();
  const { hiveId } = useLocalSearchParams<{ hiveId: string }>();

  // Form state
  const [weather, setWeather] = useState('');
  const [inspector, setInspector] = useState('');
  const [notes, setNotes] = useState('');
  const [voiceTranscript, setVoiceTranscript] = useState('');

  // Quick log fields
  const [queenSeen, setQueenSeen] = useState<boolean | null>(null);
  const [eggsSeen, setEggsSeen] = useState<boolean | null>(null);
  const [swarmSigns, setSwarmSigns] = useState<boolean | null>(null);
  const [populationStrength, setPopulationStrength] = useState<number>(5);
  const [varroa, setVarroa] = useState('');

  // Camera & voice state
  const [showCamera, setShowCamera] = useState(false);
  const [cameraPermission, requestCameraPermission] = useCameraPermissions();
  const [recording, setRecording] = useState<Audio.Recording | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const cameraRef = useRef<CameraView>(null);

  const [saving, setSaving] = useState(false);

  const handleTakePhoto = async () => {
    if (!cameraPermission?.granted) {
      const { granted } = await requestCameraPermission();
      if (!granted) {
        Alert.alert('Permission Denied', 'Camera access is required to take photos.');
        return;
      }
    }
    setShowCamera(true);
  };

  const handleCapture = async () => {
    if (!cameraRef.current) return;

    try {
      const photo = await cameraRef.current.takePictureAsync({ quality: 0.7 });
      if (photo?.uri) {
        Alert.alert('Photo Captured', 'Photo will be attached to inspection');
        // In full implementation, store photo path in state and save to inspection
        setShowCamera(false);
      }
    } catch (error) {
      console.error('Failed to take photo:', error);
      Alert.alert('Error', 'Failed to capture photo');
    }
  };

  const handleStartRecording = async () => {
    try {
      const { granted } = await Audio.requestPermissionsAsync();
      if (!granted) {
        Alert.alert('Permission Denied', 'Microphone access is required to record voice notes.');
        return;
      }

      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      const { recording } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );

      setRecording(recording);
      setIsRecording(true);
    } catch (error) {
      console.error('Failed to start recording:', error);
      Alert.alert('Error', 'Failed to start voice recording');
    }
  };

  const handleStopRecording = async () => {
    if (!recording) return;

    try {
      setIsRecording(false);
      await recording.stopAndUnloadAsync();
      const uri = recording.getURI();

      if (uri) {
        // In full implementation, you would transcribe the audio here
        // For MVP, we'll just note that voice was recorded
        setVoiceTranscript('Voice note recorded (transcription not implemented in MVP)');
        Alert.alert('Voice Note Saved', 'Voice recording saved. Add transcription for better structuring.');
      }

      setRecording(null);
    } catch (error) {
      console.error('Failed to stop recording:', error);
    }
  };

  const handleSave = async () => {
    if (!hiveId) {
      Alert.alert('Error', 'No hive selected');
      return;
    }

    if (!notes && !voiceTranscript) {
      Alert.alert('Missing Information', 'Please add some notes before saving.');
      return;
    }

    setSaving(true);

    try {
      // Create inspection
      const inspection = await inspectionService.create({
        hive_id: hiveId,
        datetime: new Date().toISOString(),
        weather: weather || null,
        inspector: inspector || null,
        freeform_notes: notes || null,
        voice_transcript: voiceTranscript || null,
      });

      // Create quick log findings if provided
      if (queenSeen !== null || eggsSeen !== null || swarmSigns !== null || varroa) {
        await inspectionService.createFindings({
          inspection_id: inspection.id,
          brood_pattern: null,
          eggs_seen: eggsSeen,
          queen_seen: queenSeen,
          stores_honey: null,
          stores_pollen: null,
          population_strength: populationStrength !== 5 ? populationStrength : null,
          temperament: null,
          swarm_signs: swarmSigns,
          swarm_signs_detail: null,
          pests_observed: varroa || null,
          varroa_count_method: null,
          varroa_count_value: null,
          disease_flags: null,
          equipment_changes: null,
        });
      }

      // Navigate to review screen to structure the inspection
      router.replace({
        pathname: '/inspection/review',
        params: { inspectionId: inspection.id },
      });
    } catch (error) {
      console.error('Failed to save inspection:', error);
      Alert.alert('Error', 'Failed to save inspection');
      setSaving(false);
    }
  };

  if (showCamera) {
    return (
      <View style={styles.cameraContainer}>
        <CameraView style={styles.camera} ref={cameraRef} facing="back">
          <View style={styles.cameraControls}>
            <TouchableOpacity style={styles.cameraButton} onPress={handleCapture}>
              <Text style={styles.cameraButtonText}>📷 Capture</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.cameraButton, styles.cancelButton]}
              onPress={() => setShowCamera(false)}
            >
              <Text style={styles.cameraButtonText}>✕ Cancel</Text>
            </TouchableOpacity>
          </View>
        </CameraView>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Quick Log</Text>
        <Text style={styles.hint}>Tap to record key observations</Text>

        <View style={styles.quickLogRow}>
          <Text style={styles.label}>Queen Seen:</Text>
          <View style={styles.buttonGroup}>
            <TouchableOpacity
              style={[styles.toggleButton, queenSeen === true && styles.toggleButtonActive]}
              onPress={() => setQueenSeen(true)}
            >
              <Text style={[styles.toggleText, queenSeen === true && styles.toggleTextActive]}>
                Yes
              </Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.toggleButton, queenSeen === false && styles.toggleButtonActive]}
              onPress={() => setQueenSeen(false)}
            >
              <Text style={[styles.toggleText, queenSeen === false && styles.toggleTextActive]}>
                No
              </Text>
            </TouchableOpacity>
          </View>
        </View>

        <View style={styles.quickLogRow}>
          <Text style={styles.label}>Eggs Seen:</Text>
          <View style={styles.buttonGroup}>
            <TouchableOpacity
              style={[styles.toggleButton, eggsSeen === true && styles.toggleButtonActive]}
              onPress={() => setEggsSeen(true)}
            >
              <Text style={[styles.toggleText, eggsSeen === true && styles.toggleTextActive]}>
                Yes
              </Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.toggleButton, eggsSeen === false && styles.toggleButtonActive]}
              onPress={() => setEggsSeen(false)}
            >
              <Text style={[styles.toggleText, eggsSeen === false && styles.toggleTextActive]}>
                No
              </Text>
            </TouchableOpacity>
          </View>
        </View>

        <View style={styles.quickLogRow}>
          <Text style={styles.label}>Swarm Signs:</Text>
          <View style={styles.buttonGroup}>
            <TouchableOpacity
              style={[styles.toggleButton, swarmSigns === true && styles.toggleButtonActive]}
              onPress={() => setSwarmSigns(true)}
            >
              <Text style={[styles.toggleText, swarmSigns === true && styles.toggleTextActive]}>
                Yes
              </Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.toggleButton, swarmSigns === false && styles.toggleButtonActive]}
              onPress={() => setSwarmSigns(false)}
            >
              <Text style={[styles.toggleText, swarmSigns === false && styles.toggleTextActive]}>
                No
              </Text>
            </TouchableOpacity>
          </View>
        </View>

        <View style={styles.sliderContainer}>
          <Text style={styles.label}>Population Strength: {populationStrength}/10</Text>
          <View style={styles.strengthButtons}>
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((val) => (
              <TouchableOpacity
                key={val}
                style={[
                  styles.strengthButton,
                  populationStrength >= val && styles.strengthButtonActive,
                ]}
                onPress={() => setPopulationStrength(val)}
              >
                <Text style={styles.strengthButtonText}>{val}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Details (Optional)</Text>

        <Text style={styles.label}>Weather</Text>
        <TextInput
          style={styles.input}
          value={weather}
          onChangeText={setWeather}
          placeholder="e.g., Sunny, 22°C"
          placeholderTextColor="#999"
        />

        <Text style={styles.label}>Inspector</Text>
        <TextInput
          style={styles.input}
          value={inspector}
          onChangeText={setInspector}
          placeholder="Your name"
          placeholderTextColor="#999"
        />

        <Text style={styles.label}>Varroa / Pests</Text>
        <TextInput
          style={styles.input}
          value={varroa}
          onChangeText={setVarroa}
          placeholder="e.g., Low varroa levels"
          placeholderTextColor="#999"
        />
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Notes</Text>

        <TextInput
          style={styles.notesInput}
          value={notes}
          onChangeText={setNotes}
          placeholder="Detailed observations, brood pattern, stores, temperament, etc."
          placeholderTextColor="#999"
          multiline
          numberOfLines={6}
          textAlignVertical="top"
        />

        <View style={styles.mediaButtons}>
          <TouchableOpacity style={styles.mediaButton} onPress={handleTakePhoto}>
            <Text style={styles.mediaButtonText}>📷 Photo</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.mediaButton, isRecording && styles.mediaButtonRecording]}
            onPress={isRecording ? handleStopRecording : handleStartRecording}
          >
            <Text style={styles.mediaButtonText}>
              {isRecording ? '⏹️ Stop' : '🎤 Voice'}
            </Text>
          </TouchableOpacity>
        </View>

        {voiceTranscript && (
          <View style={styles.transcriptContainer}>
            <Text style={styles.transcriptLabel}>Voice Note:</Text>
            <Text style={styles.transcriptText}>{voiceTranscript}</Text>
          </View>
        )}
      </View>

      <View style={styles.bottomButtons}>
        <TouchableOpacity
          style={[styles.saveButton, saving && styles.saveButtonDisabled]}
          onPress={handleSave}
          disabled={saving}
        >
          <Text style={styles.saveButtonText}>
            {saving ? 'Saving...' : '✓ Save & Review'}
          </Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
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
    marginBottom: 8,
  },
  hint: {
    fontSize: 12,
    color: '#999',
    marginBottom: 16,
  },
  quickLogRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
    minHeight: 44,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  buttonGroup: {
    flexDirection: 'row',
    gap: 8,
  },
  toggleButton: {
    paddingHorizontal: 24,
    paddingVertical: 10,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#DDD',
    backgroundColor: '#fff',
    minWidth: 70,
    alignItems: 'center',
  },
  toggleButtonActive: {
    borderColor: '#FFA500',
    backgroundColor: '#FFA500',
  },
  toggleText: {
    fontSize: 14,
    color: '#666',
    fontWeight: '600',
  },
  toggleTextActive: {
    color: '#fff',
  },
  sliderContainer: {
    marginTop: 8,
  },
  strengthButtons: {
    flexDirection: 'row',
    gap: 4,
    marginTop: 8,
  },
  strengthButton: {
    flex: 1,
    paddingVertical: 8,
    backgroundColor: '#f0f0f0',
    borderRadius: 6,
    alignItems: 'center',
    minHeight: 44,
    justifyContent: 'center',
  },
  strengthButtonActive: {
    backgroundColor: '#FFA500',
  },
  strengthButtonText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#666',
  },
  input: {
    borderWidth: 1,
    borderColor: '#DDD',
    borderRadius: 8,
    padding: 12,
    fontSize: 14,
    marginBottom: 16,
    backgroundColor: '#fff',
    minHeight: 44,
  },
  notesInput: {
    borderWidth: 1,
    borderColor: '#DDD',
    borderRadius: 8,
    padding: 12,
    fontSize: 14,
    marginBottom: 16,
    backgroundColor: '#fff',
    minHeight: 120,
  },
  mediaButtons: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 16,
  },
  mediaButton: {
    flex: 1,
    paddingVertical: 14,
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
    alignItems: 'center',
    minHeight: 50,
    justifyContent: 'center',
  },
  mediaButtonRecording: {
    backgroundColor: '#F44336',
  },
  mediaButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  transcriptContainer: {
    padding: 12,
    backgroundColor: '#f9f9f9',
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#FFA500',
  },
  transcriptLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: '#666',
    marginBottom: 4,
  },
  transcriptText: {
    fontSize: 14,
    color: '#333',
  },
  bottomButtons: {
    padding: 16,
    paddingBottom: 32,
  },
  saveButton: {
    backgroundColor: '#4CAF50',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    minHeight: 56,
    justifyContent: 'center',
  },
  saveButtonDisabled: {
    backgroundColor: '#CCC',
  },
  saveButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  cameraContainer: {
    flex: 1,
  },
  camera: {
    flex: 1,
  },
  cameraControls: {
    flex: 1,
    backgroundColor: 'transparent',
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'flex-end',
    paddingBottom: 50,
  },
  cameraButton: {
    backgroundColor: '#FFA500',
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 10,
    minHeight: 50,
    minWidth: 120,
    justifyContent: 'center',
    alignItems: 'center',
  },
  cancelButton: {
    backgroundColor: '#F44336',
  },
  cameraButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
