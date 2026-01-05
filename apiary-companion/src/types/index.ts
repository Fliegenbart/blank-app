// Core entity types for Apiary Companion

export interface User {
  id: string;
  email: string | null;
  created_at: string;
  is_local_only: boolean;
  preferences: string;
}

export interface Apiary {
  id: string;
  user_id: string;
  name: string;
  location_approx: string | null;
  latitude: number | null;
  longitude: number | null;
  timezone: string;
  created_at: string;
}

export interface Hive {
  id: string;
  apiary_id: string;
  hive_code: string;
  hive_type: string | null;
  start_date: string;
  status: 'active' | 'inactive' | 'dead' | 'sold';
  notes: string | null;
  created_at: string;
}

export interface Colony {
  id: string;
  hive_id: string;
  queen_year: number | null;
  queen_origin: string | null;
  temperament_notes: string | null;
  status: 'active' | 'requeened' | 'dead';
  created_at: string;
}

export interface Inspection {
  id: string;
  hive_id: string;
  datetime: string;
  weather: string | null;
  inspector: string | null;
  freeform_notes: string | null;
  voice_transcript: string | null;
  is_structured: boolean;
  created_at: string;
}

export interface InspectionFindings {
  id: string;
  inspection_id: string;
  brood_pattern: string | null;
  eggs_seen: boolean | null;
  queen_seen: boolean | null;
  stores_honey: number | null;
  stores_pollen: number | null;
  population_strength: number | null;
  temperament: string | null;
  swarm_signs: boolean | null;
  swarm_signs_detail: string | null;
  pests_observed: string | null;
  varroa_count_method: string | null;
  varroa_count_value: number | null;
  disease_flags: string | null;
  equipment_changes: string | null;
}

export interface Task {
  id: string;
  apiary_id: string | null;
  hive_id: string | null;
  title: string;
  description: string | null;
  due_date: string | null;
  priority: 'low' | 'medium' | 'high';
  status: 'pending' | 'completed' | 'cancelled';
  source: 'manual' | 'inspection_suggestion' | 'seasonal_plan';
  created_at: string;
  completed_at: string | null;
}

export interface Treatment {
  id: string;
  hive_id: string;
  type: string;
  product_name: string;
  start_date: string;
  end_date: string | null;
  dosage_notes: string | null;
  compliance_notes: string | null;
  effectiveness_notes: string | null;
  created_at: string;
}

export interface Harvest {
  id: string;
  hive_id: string;
  date: string;
  honey_kg: number;
  supers_count: number | null;
  notes: string | null;
  created_at: string;
}

export interface InventoryItem {
  id: string;
  apiary_id: string;
  category: string;
  name: string;
  quantity: number;
  unit: string;
  reorder_level: number | null;
  created_at: string;
}

export interface Attachment {
  id: string;
  inspection_id: string | null;
  file_path: string;
  mime_type: string;
  created_at: string;
}

export interface InspectionStructuredData {
  findings: Partial<Omit<InspectionFindings, 'id' | 'inspection_id'>>;
  suggestedTasks: Array<{
    title: string;
    description: string;
    dueInDays: number;
    priority: 'low' | 'medium' | 'high';
  }>;
  confidence: number;
}

export interface SeasonalPlan {
  id: string;
  apiary_id: string;
  region: 'northern_europe' | 'central_europe' | 'southern_europe';
  start_month: number;
  is_active: boolean;
  created_at: string;
}
