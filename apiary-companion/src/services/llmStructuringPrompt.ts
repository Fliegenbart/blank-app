export const PROMPT_VERSION = '1.0.0';

export const SYSTEM_PROMPT = `You are an expert beekeeping assistant AI. Your task is to analyze inspection notes (either freeform text or voice transcriptions) and extract structured data about the hive condition.

Your goal is to:
1. Extract factual information about the hive inspection findings
2. Suggest actionable tasks based on the findings
3. Assess the confidence level of your extraction

Be conservative in your interpretations. If something is not explicitly mentioned or cannot be inferred with reasonable confidence, leave it as null.`;

export const USER_PROMPT_TEMPLATE = `Analyze the following beehive inspection notes and extract structured information.

**Inspection Notes:**
{{INSPECTION_NOTES}}

**Instructions:**
1. Extract inspection findings where applicable
2. Suggest 0-5 actionable tasks based on the findings (only suggest tasks that are clearly needed)
3. Provide a confidence score (0-1) for your overall extraction

**Response Format (JSON):**
{
  "findings": {
    "brood_pattern": "solid|spotty|mixed|none|null",
    "eggs_seen": true|false|null,
    "queen_seen": true|false|null,
    "stores_honey": 1-5 (scale)|null,
    "stores_pollen": 1-5 (scale)|null,
    "population_strength": 1-5 (scale)|null,
    "temperament": "calm|defensive|aggressive|null",
    "swarm_signs": true|false|null,
    "swarm_signs_detail": "description of signs|null",
    "pests_observed": "description of pests|null",
    "varroa_count_method": "sugar_roll|alcohol_wash|sticky_board|visual|null",
    "varroa_count_value": number|null,
    "disease_flags": "description of diseases|null",
    "equipment_changes": "description of changes|null"
  },
  "suggestedTasks": [
    {
      "title": "Task title",
      "description": "Detailed description",
      "dueInDays": number (how many days from now),
      "priority": "low|medium|high"
    }
  ],
  "confidence": 0.0-1.0
}

**Scaling Guidelines:**
- Honey/Pollen Stores: 1=empty, 2=low, 3=adequate, 4=good, 5=full
- Population Strength: 1=very weak, 2=weak, 3=moderate, 4=strong, 5=very strong

**Task Suggestion Guidelines:**
- Only suggest tasks that are clearly indicated by the findings
- Be specific in task descriptions
- Set realistic due dates based on urgency
- Prioritize tasks appropriately (high=urgent/critical, medium=important, low=routine)

Common tasks to consider:
- Feeding if stores are low (< 3)
- Adding supers if honey stores high and flow season
- Swarm prevention if swarm signs detected
- Pest/disease treatment if issues observed
- Equipment maintenance/repairs
- Requeening if queen issues
- Varroa treatment if counts are high

Now analyze the inspection notes and provide the structured JSON response:`;

export function formatPrompt(inspectionNotes: string): string {
  return USER_PROMPT_TEMPLATE.replace('{{INSPECTION_NOTES}}', inspectionNotes);
}

export const EXAMPLE_INSPECTION_NOTES = `Weather was sunny, about 20°C. Opened hive #3 at 2pm.

Queen was spotted on frame 4, looking good and actively laying. Saw eggs and young larvae. Brood pattern looks mostly solid with a few gaps here and there.

Bees seemed pretty calm today, no defensive behavior. Population looks strong, probably 7-8 frames covered with bees.

Honey stores are decent - about 3 frames capped on the sides. Pollen coming in nicely too.

Didn't see any obvious signs of disease or pests. Did a quick visual check for varroa - didn't see any on bees but probably should do a proper count soon.

Added a queen excluder and a super since the flow is starting to pick up.`;

export const EXAMPLE_STRUCTURED_OUTPUT = {
  findings: {
    brood_pattern: 'solid',
    eggs_seen: true,
    queen_seen: true,
    stores_honey: 3,
    stores_pollen: 4,
    population_strength: 4,
    temperament: 'calm',
    swarm_signs: false,
    swarm_signs_detail: null,
    pests_observed: null,
    varroa_count_method: null,
    varroa_count_value: null,
    disease_flags: null,
    equipment_changes: 'Added queen excluder and honey super',
  },
  suggestedTasks: [
    {
      title: 'Perform varroa mite count',
      description:
        'Complete a sugar roll or alcohol wash to get accurate varroa count. Visual inspection is not sufficient.',
      dueInDays: 7,
      priority: 'medium',
    },
    {
      title: 'Monitor super filling',
      description:
        'Check the new super in 1-2 weeks to see if bees are drawing comb and storing honey.',
      dueInDays: 10,
      priority: 'low',
    },
  ],
  confidence: 0.9,
};
