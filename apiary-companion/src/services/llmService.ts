import { InspectionStructuredData } from '../types';
import { SYSTEM_PROMPT, formatPrompt, PROMPT_VERSION } from './llmStructuringPrompt';

export interface LLMConfig {
  apiKey: string;
  model?: string;
  baseUrl?: string;
}

export interface LLMResponse {
  data: InspectionStructuredData;
  rawResponse: string;
  promptVersion: string;
  modelUsed: string;
  error?: string;
}

// Default to Anthropic Claude
const DEFAULT_MODEL = 'claude-3-5-sonnet-20241022';
const DEFAULT_BASE_URL = 'https://api.anthropic.com/v1/messages';

/**
 * Call LLM to structure inspection notes
 * Supports Anthropic Claude API (default) or OpenAI-compatible APIs
 */
export async function structureInspectionNotes(
  inspectionNotes: string,
  config: LLMConfig
): Promise<LLMResponse> {
  const model = config.model || DEFAULT_MODEL;
  const baseUrl = config.baseUrl || DEFAULT_BASE_URL;

  try {
    const userPrompt = formatPrompt(inspectionNotes);

    // Detect if using Anthropic or OpenAI-compatible API
    const isAnthropic = baseUrl.includes('anthropic.com');

    let response: Response;

    if (isAnthropic) {
      // Anthropic API format
      response = await fetch(baseUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': config.apiKey,
          'anthropic-version': '2023-06-01',
        },
        body: JSON.stringify({
          model,
          max_tokens: 2000,
          messages: [
            {
              role: 'user',
              content: `${SYSTEM_PROMPT}\n\n${userPrompt}`,
            },
          ],
        }),
      });
    } else {
      // OpenAI-compatible API format
      response = await fetch(baseUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${config.apiKey}`,
        },
        body: JSON.stringify({
          model,
          messages: [
            {
              role: 'system',
              content: SYSTEM_PROMPT,
            },
            {
              role: 'user',
              content: userPrompt,
            },
          ],
          temperature: 0.3,
          max_tokens: 2000,
        }),
      });
    }

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`LLM API error: ${response.status} - ${errorText}`);
    }

    const responseData = await response.json();

    // Extract content based on API format
    let content: string;
    if (isAnthropic) {
      content = responseData.content[0].text;
    } else {
      content = responseData.choices[0].message.content;
    }

    // Parse the JSON response
    const structuredData = parseStructuredResponse(content);

    return {
      data: structuredData,
      rawResponse: content,
      promptVersion: PROMPT_VERSION,
      modelUsed: model,
    };
  } catch (error) {
    console.error('Error calling LLM service:', error);
    return {
      data: {
        findings: {},
        suggestedTasks: [],
        confidence: 0,
      },
      rawResponse: '',
      promptVersion: PROMPT_VERSION,
      modelUsed: model,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

/**
 * Parse the LLM response and extract structured data
 * Handles various response formats and validates the data
 */
function parseStructuredResponse(content: string): InspectionStructuredData {
  try {
    // Try to extract JSON from the response (LLM might include extra text)
    const jsonMatch = content.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
      throw new Error('No JSON found in response');
    }

    const parsed = JSON.parse(jsonMatch[0]);

    // Validate and normalize the response
    const structuredData: InspectionStructuredData = {
      findings: {},
      suggestedTasks: [],
      confidence: 0,
    };

    // Extract findings
    if (parsed.findings && typeof parsed.findings === 'object') {
      structuredData.findings = parsed.findings;
    }

    // Extract suggested tasks
    if (Array.isArray(parsed.suggestedTasks)) {
      structuredData.suggestedTasks = parsed.suggestedTasks
        .filter(
          (task: any) =>
            task &&
            typeof task === 'object' &&
            task.title &&
            task.description &&
            typeof task.dueInDays === 'number' &&
            ['low', 'medium', 'high'].includes(task.priority)
        )
        .map((task: any) => ({
          title: String(task.title),
          description: String(task.description),
          dueInDays: Number(task.dueInDays),
          priority: task.priority as 'low' | 'medium' | 'high',
        }));
    }

    // Extract confidence
    if (typeof parsed.confidence === 'number') {
      structuredData.confidence = Math.max(0, Math.min(1, parsed.confidence));
    }

    return structuredData;
  } catch (error) {
    console.error('Error parsing LLM response:', error);
    return {
      findings: {},
      suggestedTasks: [],
      confidence: 0,
    };
  }
}

/**
 * Test the LLM service with example data
 */
export async function testLLMService(config: LLMConfig): Promise<boolean> {
  const testNotes = `Quick inspection. Queen seen, eggs present. Stores look good. Added a super.`;

  try {
    const result = await structureInspectionNotes(testNotes, config);
    return !result.error && result.data.confidence > 0;
  } catch (error) {
    console.error('LLM service test failed:', error);
    return false;
  }
}

/**
 * Validate LLM API configuration
 */
export function validateLLMConfig(config: Partial<LLMConfig>): {
  valid: boolean;
  errors: string[];
} {
  const errors: string[] = [];

  if (!config.apiKey || config.apiKey.trim() === '') {
    errors.push('API key is required');
  }

  if (config.baseUrl) {
    try {
      new URL(config.baseUrl);
    } catch {
      errors.push('Invalid base URL format');
    }
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}
