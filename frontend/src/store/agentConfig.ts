import { create } from 'zustand'

import type { LiteLLMConfig, MCPMode, ScaffoldRequest, SessionBackend } from '@/types'

function cloneConfig(config: ScaffoldRequest): ScaffoldRequest {
  return JSON.parse(JSON.stringify(config)) as ScaffoldRequest
}

export const DEFAULT_CONFIG: ScaffoldRequest = {
  projectName: 'cd-ladder-advisor',
  description: 'Default CD Ladder Advisor scaffold for AgentForge.',
  rootAgent: {
    name: 'CDLadderOrchestrator',
    agentType: 'sequential',
    instructions:
      'Coordinate the CD ladder workflow from profile lookup through recommendation.',
    subAgents: [
      {
        name: 'CustomerProfileAgent',
        agentType: 'llm',
        instructions: 'Gather customer profile and account context.',
        model: 'gemini/gemini-2.0-flash',
        tools: [
          { name: 'get_customer_profile', description: 'Fetch customer profile.' },
          { name: 'get_account_balances', description: 'Fetch account balances.' },
        ],
      },
      {
        name: 'RateResearchAgent',
        agentType: 'llm',
        instructions: 'Collect current CD rates.',
        model: 'gemini/gemini-2.0-flash',
        tools: [{ name: 'get_current_cd_rates', description: 'Get current CD rates.' }],
      },
      {
        name: 'LadderCalculatorAgent',
        agentType: 'llm',
        instructions: 'Calculate ladder split recommendations.',
        model: 'gemini/gemini-2.0-flash',
        tools: [
          {
            name: 'calculate_ladder_splits',
            description: 'Compute ladder allocations across terms.',
            isDeterministic: true,
          },
        ],
      },
      {
        name: 'ValidationAgent',
        agentType: 'llm',
        instructions: 'Validate recommendations and policy boundaries.',
        model: 'gemini/gemini-2.0-flash',
        tools: [
          {
            name: 'validate_recommendation',
            description: 'Validate recommendation integrity.',
          },
          {
            name: 'check_regulatory_limits',
            description: 'Apply regulatory guardrails.',
            isDeterministic: true,
          },
        ],
      },
      {
        name: 'NotificationAgent',
        agentType: 'llm',
        instructions: 'Format final recommendation output.',
        model: 'gemini/gemini-2.0-flash',
        tools: [
          {
            name: 'format_recommendation_output',
            description: 'Create presentation-ready recommendation text.',
          },
        ],
      },
    ],
  },
  mcpServers: [
    {
      name: 'banking-core',
      mode: 'stdio',
      enabled: true,
      command: 'python',
      args: ['-m', 'banking_core_mcp'],
      env: {
        BANK_ENV: 'sandbox',
      },
    },
  ],
  litellm: {
    apiBase: 'http://127.0.0.1:4000/v1',
    apiKeyEnv: 'LITELLM_API_KEY',
    model: 'gemini/gemini-2.0-flash',
    provider: 'openai',
    maxTokens: 1024,
    temperature: 0.2,
  },
  session: {
    backend: 'memory',
    sessionTtlMinutes: 60,
  },
  callbacks: {
    beforeToolCall: true,
    afterToolCall: true,
    beforeAgentCall: true,
    afterAgentCall: false,
  },
}

export const EMPTY_CONFIG: ScaffoldRequest = {
  projectName: 'new-agent-project',
  description: 'New agent scaffold.',
  rootAgent: {
    name: 'RootAgent',
    agentType: 'sequential',
    instructions: 'Describe the orchestration goal for this project.',
    subAgents: [],
    tools: [],
  },
  mcpServers: [],
  litellm: {
    apiBase: 'http://127.0.0.1:4000/v1',
    apiKeyEnv: 'LITELLM_API_KEY',
    model: 'gemini/gemini-2.0-flash',
    provider: 'openai',
    maxTokens: 1024,
    temperature: 0.2,
  },
  session: {
    backend: 'memory',
    sessionTtlMinutes: 60,
  },
  callbacks: {
    beforeToolCall: true,
    afterToolCall: true,
    beforeAgentCall: true,
    afterAgentCall: false,
  },
}

interface AgentConfigState {
  config: ScaffoldRequest
  setConfig: (config: ScaffoldRequest) => void
  resetConfig: () => void
  loadBootstrapExample: () => void
  setProjectName: (projectName: string) => void
  setRootAgentName: (name: string) => void
  addMcpServer: () => void
  updateMcpServer: (
    index: number,
    patch: Partial<ScaffoldRequest['mcpServers'][number]>
  ) => void
  setMcpServerMode: (index: number, mode: MCPMode) => void
  setSessionBackend: (backend: SessionBackend) => void
  setSessionDbUrl: (dbUrl: string) => void
  updateLiteLLMField: <K extends keyof LiteLLMConfig>(
    field: K,
    value: LiteLLMConfig[K]
  ) => void
}

export const useAgentConfigStore = create<AgentConfigState>((set) => ({
  config: cloneConfig(DEFAULT_CONFIG),
  setConfig: (config) => set({ config }),
  resetConfig: () => set({ config: cloneConfig(EMPTY_CONFIG) }),
  loadBootstrapExample: () => set({ config: cloneConfig(DEFAULT_CONFIG) }),
  setProjectName: (projectName) =>
    set((state) => ({ config: { ...state.config, projectName } })),
  setRootAgentName: (name) =>
    set((state) => ({
      config: {
        ...state.config,
        rootAgent: {
          ...state.config.rootAgent,
          name,
        },
      },
    })),
  addMcpServer: () =>
    set((state) => ({
      config: {
        ...state.config,
        mcpServers: [
          ...state.config.mcpServers,
          {
            name: `mcp-server-${state.config.mcpServers.length + 1}`,
            mode: 'sse',
            enabled: true,
            url: 'http://localhost:9000/sse',
            env: {},
            args: [],
          },
        ],
      },
    })),
  updateMcpServer: (index, patch) =>
    set((state) => ({
      config: {
        ...state.config,
        mcpServers: state.config.mcpServers.map((server, serverIndex) =>
          serverIndex === index ? { ...server, ...patch } : server
        ),
      },
    })),
  setMcpServerMode: (index, mode) =>
    set((state) => ({
      config: {
        ...state.config,
        mcpServers: state.config.mcpServers.map((server, serverIndex) =>
          serverIndex === index
            ? {
                ...server,
                mode,
                command: mode === 'stdio' ? server.command ?? 'python' : undefined,
                args: mode === 'stdio' ? server.args ?? ['-m', 'banking_core_mcp'] : [],
                url: mode === 'sse' ? server.url ?? 'http://localhost:9000/sse' : undefined,
              }
            : server
        ),
      },
    })),
  setSessionBackend: (backend) =>
    set((state) => ({
      config: {
        ...state.config,
        session: {
          ...state.config.session,
          backend,
          dbUrl:
            backend === 'postgres'
              ? state.config.session.dbUrl ?? 'postgresql://user:pass@localhost:5432/agentforge'
              : undefined,
        },
      },
    })),
  setSessionDbUrl: (dbUrl) =>
    set((state) => ({
      config: {
        ...state.config,
        session: {
          ...state.config.session,
          dbUrl,
        },
      },
    })),
  updateLiteLLMField: (field, value) =>
    set((state) => ({
      config: {
        ...state.config,
        litellm: {
          ...state.config.litellm,
          [field]: value,
        },
      },
    })),
}))
