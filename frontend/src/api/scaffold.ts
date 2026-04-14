import axios from 'axios'

import type {
  AgentDefinition,
  HealthResponse,
  ScaffoldRequest,
  ScaffoldResponse,
  ToolDefinition,
} from '@/types'

const API_HOST =
  typeof window === 'undefined' ? '127.0.0.1' : window.location.hostname || '127.0.0.1'
const API_BASE_URL = `http://${API_HOST}:8000`

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 20_000,
})

const mapTool = (tool: ToolDefinition): Record<string, unknown> => ({
  name: tool.name,
  description: tool.description,
  is_deterministic: Boolean(tool.isDeterministic),
  parameters_schema: tool.parametersSchema ?? {},
})

const mapAgent = (agent: AgentDefinition): Record<string, unknown> => ({
  name: agent.name,
  agent_type: agent.agentType,
  instructions: agent.instructions,
  model: agent.model,
  tools: (agent.tools ?? []).map(mapTool),
  sub_agents: (agent.subAgents ?? []).map(mapAgent),
})

const toBackendPayload = (config: ScaffoldRequest): Record<string, unknown> => ({
  project_name: config.projectName,
  description: config.description,
  root_agent: mapAgent(config.rootAgent),
  mcp_servers: config.mcpServers.map((server) => ({
    name: server.name,
    mode: server.mode,
    enabled: server.enabled ?? true,
    command: server.command,
    args: server.args ?? [],
    env: server.env ?? {},
    url: server.url,
  })),
  litellm: {
    api_base: config.litellm.apiBase,
    api_key_env: config.litellm.apiKeyEnv,
    model: config.litellm.model,
    provider: config.litellm.provider,
    max_tokens: config.litellm.maxTokens,
    temperature: config.litellm.temperature,
  },
  session: {
    backend: config.session.backend,
    db_url: config.session.dbUrl,
    session_ttl_minutes: config.session.sessionTtlMinutes,
  },
  callbacks: {
    before_tool_call: config.callbacks.beforeToolCall,
    after_tool_call: config.callbacks.afterToolCall,
    before_agent_call: config.callbacks.beforeAgentCall,
    after_agent_call: config.callbacks.afterAgentCall,
  },
})

const fromBackendResponse = (data: Record<string, unknown>): ScaffoldResponse => ({
  files: ((data.files as Array<{ filename: string; content: string }>) ?? []).map((file) => ({
    filename: file.filename,
    content: file.content,
  })),
  downloadToken: (data.download_token as string | null) ?? null,
})

export const generateProject = async (
  config: ScaffoldRequest
): Promise<ScaffoldResponse> => {
  const response = await apiClient.post<Record<string, unknown>>(
    '/api/generate',
    toBackendPayload(config)
  )
  return fromBackendResponse(response.data)
}

export const downloadZip = (token: string): void => {
  window.open(`${API_BASE_URL}/api/download/${token}`, '_blank', 'noopener,noreferrer')
}

export const checkHealth = async (): Promise<HealthResponse> => {
  const response = await apiClient.get<HealthResponse>('/health')
  return response.data
}
