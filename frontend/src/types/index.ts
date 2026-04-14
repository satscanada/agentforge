export type AgentType = 'llm' | 'sequential' | 'parallel' | 'loop'

export type SessionBackend = 'memory' | 'postgres'

export type MCPMode = 'disabled' | 'stdio' | 'sse'

export interface ToolDefinition {
  name: string
  description: string
  isDeterministic?: boolean
  parametersSchema?: Record<string, unknown>
}

export interface MCPServerConfig {
  name: string
  mode: MCPMode
  enabled?: boolean
  command?: string
  args?: string[]
  env?: Record<string, string>
  url?: string
}

export interface AgentDefinition {
  name: string
  agentType: AgentType
  instructions: string
  model?: string
  tools?: ToolDefinition[]
  subAgents?: AgentDefinition[]
}

export interface LiteLLMConfig {
  apiBase: string
  apiKeyEnv: string
  model: string
  provider: string
  maxTokens: number
  temperature: number
}

export interface SessionConfig {
  backend: SessionBackend
  dbUrl?: string
  sessionTtlMinutes: number
}

export interface CallbackConfig {
  beforeToolCall: boolean
  afterToolCall: boolean
  beforeAgentCall: boolean
  afterAgentCall: boolean
}

export interface ScaffoldRequest {
  projectName: string
  description: string
  rootAgent: AgentDefinition
  mcpServers: MCPServerConfig[]
  litellm: LiteLLMConfig
  session: SessionConfig
  callbacks: CallbackConfig
}

export interface GeneratedFile {
  filename: string
  content: string
}

export interface ScaffoldResponse {
  files: GeneratedFile[]
  downloadToken: string | null
}

export interface HealthResponse {
  status: string
  service: string
  version: string
}

export interface TestRunStep {
  agentName: string
  agentType: AgentType
  depth: number
  mode: string
  summary: string
  toolsUsed: string[]
  output: string
}

export interface TestRunResponse {
  status: string
  projectName: string
  rootAgent: string
  inputMessage: string
  finalOutput: string
  steps: TestRunStep[]
  warnings: string[]
}
