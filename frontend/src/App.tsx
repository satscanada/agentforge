import {
  startTransition,
  useDeferredValue,
  useEffect,
  useEffectEvent,
  useMemo,
  useState,
} from 'react'

import './App.css'

import { DownloadButton } from '@/components/output/DownloadButton'
import { CodeViewer } from '@/components/output/CodeViewer'
import { AgentCard } from '@/components/topology/AgentCard'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { TooltipProvider } from '@/components/ui/tooltip'
import { useAgentConfigStore } from '@/store/agentConfig'
import { checkHealth, downloadZip, generateProject } from '@/api/scaffold'
import type {
  GeneratedFile,
  HealthResponse,
  MCPServerConfig,
  MCPMode,
  ScaffoldRequest,
} from '@/types'

const HEALTH_POLL_INTERVAL_MS = 30_000

function App() {
  const config = useAgentConfigStore((state) => state.config)
  const setProjectName = useAgentConfigStore((state) => state.setProjectName)
  const setRootAgentName = useAgentConfigStore((state) => state.setRootAgentName)
  const addMcpServer = useAgentConfigStore((state) => state.addMcpServer)
  const updateMcpServer = useAgentConfigStore((state) => state.updateMcpServer)
  const setMcpServerMode = useAgentConfigStore((state) => state.setMcpServerMode)
  const setSessionBackend = useAgentConfigStore((state) => state.setSessionBackend)
  const setSessionDbUrl = useAgentConfigStore((state) => state.setSessionDbUrl)
  const updateLiteLLMField = useAgentConfigStore((state) => state.updateLiteLLMField)

  const deferredConfig = useDeferredValue(config)
  const [generatedFiles, setGeneratedFiles] = useState<GeneratedFile[]>(() =>
    createPreviewFiles(config)
  )
  const [downloadToken, setDownloadToken] = useState<string | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [isHealthy, setIsHealthy] = useState(false)

  const livePreview = useMemo(
    () => createPreviewFiles(deferredConfig),
    [deferredConfig]
  )

  const pollHealth = useEffectEvent(async () => {
    try {
      const nextHealth = await checkHealth()
      setHealth(nextHealth)
      setIsHealthy(nextHealth.status === 'ok')
    } catch {
      setHealth(null)
      setIsHealthy(false)
    }
  })

  useEffect(() => {
    void pollHealth()
    const intervalId = window.setInterval(() => {
      void pollHealth()
    }, HEALTH_POLL_INTERVAL_MS)
    return () => window.clearInterval(intervalId)
  }, [pollHealth])

  useEffect(() => {
    if (downloadToken !== null) {
      return
    }
    startTransition(() => {
      setGeneratedFiles(livePreview)
    })
  }, [downloadToken, livePreview])

  const handleGenerate = async () => {
    setIsGenerating(true)
    try {
      const response = await generateProject(config)
      startTransition(() => {
        setGeneratedFiles(response.files)
        setDownloadToken(response.downloadToken)
      })
    } finally {
      setIsGenerating(false)
    }
  }

  const handleDownload = () => {
    if (downloadToken !== null) {
      downloadZip(downloadToken)
    }
  }

  return (
    <TooltipProvider>
      <div className="app-shell">
        <header className="app-header">
          <div>
            <p className="eyebrow">AgentForge Studio</p>
            <h1>Topology Builder</h1>
          </div>
          <div className="header-controls">
            <div className="health-pill">
              <span className={`health-dot ${isHealthy ? 'is-online' : 'is-offline'}`} />
              <span>{isHealthy ? 'Backend Healthy' : 'Backend Offline'}</span>
              <small>{health?.version ?? 'No response'}</small>
            </div>
            <label className="project-name-field">
              <span>Project Name</span>
              <input
                type="text"
                value={config.projectName}
                onChange={(event) => setProjectName(event.target.value)}
              />
            </label>
            <Button onClick={() => void handleGenerate()} type="button">
              {isGenerating ? 'Generating...' : 'Generate'}
            </Button>
            <DownloadButton disabled={downloadToken === null} onClick={handleDownload} />
          </div>
        </header>

        <main className="workspace-grid">
          <section className="workspace-panel topology-panel">
            <div className="panel-heading">
              <p className="eyebrow">Topology</p>
              <h2>CD Ladder Agent Tree</h2>
            </div>
            <label className="panel-field">
              <span>Root Agent Name</span>
              <input
                type="text"
                value={config.rootAgent.name}
                onChange={(event) => setRootAgentName(event.target.value)}
              />
            </label>
            <AgentCard agent={deferredConfig.rootAgent} />
          </section>

          <section className="workspace-panel json-panel">
            <div className="panel-heading">
              <p className="eyebrow">State Preview</p>
              <h2>Live Zustand JSON</h2>
            </div>
            <pre className="json-preview">
              <code>{JSON.stringify(deferredConfig, null, 2)}</code>
            </pre>
          </section>

          <section className="workspace-panel output-panel">
            <div className="panel-heading">
              <p className="eyebrow">Generated Preview</p>
              <h2>Code Viewer</h2>
            </div>
            <CodeViewer files={generatedFiles} />
          </section>
        </main>

        <section className="workspace-panel bottom-panel">
          <Tabs defaultValue="mcp" className="bottom-tabs">
            <TabsList className="bottom-tabs-list" variant="line">
              <TabsTrigger value="mcp">MCP Config</TabsTrigger>
              <TabsTrigger value="session">Session</TabsTrigger>
              <TabsTrigger value="env">Env Config</TabsTrigger>
              <TabsTrigger value="litellm">LiteLLM</TabsTrigger>
            </TabsList>
            <TabsContent value="mcp" className="bottom-tab-content">
              <div className="config-toolbar">
                <p>Switch modes and add servers while watching JSON update live.</p>
                <Button onClick={() => addMcpServer()} type="button" variant="outline">
                  Add MCP Server
                </Button>
              </div>
              <div className="config-grid">
                {config.mcpServers.map((server, index) => (
                  <McpServerEditor
                    key={`${server.name}-${index}`}
                    index={index}
                    server={server}
                    onModeChange={setMcpServerMode}
                    onUpdate={updateMcpServer}
                  />
                ))}
              </div>
            </TabsContent>
            <TabsContent value="session" className="bottom-tab-content">
              <div className="config-grid one-column">
                <label className="panel-field">
                  <span>Session Backend</span>
                  <div className="radio-row">
                    <label>
                      <input
                        checked={config.session.backend === 'memory'}
                        name="session-backend"
                        onChange={() => setSessionBackend('memory')}
                        type="radio"
                      />
                      Memory
                    </label>
                    <label>
                      <input
                        checked={config.session.backend === 'postgres'}
                        name="session-backend"
                        onChange={() => setSessionBackend('postgres')}
                        type="radio"
                      />
                      Postgres
                    </label>
                  </div>
                </label>
                {config.session.backend === 'postgres' ? (
                  <label className="panel-field">
                    <span>Database URL</span>
                    <input
                      type="text"
                      value={config.session.dbUrl ?? ''}
                      onChange={(event) => setSessionDbUrl(event.target.value)}
                    />
                  </label>
                ) : null}
              </div>
            </TabsContent>
            <TabsContent value="env" className="bottom-tab-content">
              <div className="config-grid two-column">
                <LiteLLMField
                  label="API Base"
                  value={config.litellm.apiBase}
                  onChange={(value) => updateLiteLLMField('apiBase', value)}
                />
                <LiteLLMField
                  label="API Key Env"
                  value={config.litellm.apiKeyEnv}
                  onChange={(value) => updateLiteLLMField('apiKeyEnv', value)}
                />
                <LiteLLMField
                  label="Provider"
                  value={config.litellm.provider}
                  onChange={(value) => updateLiteLLMField('provider', value)}
                />
                <LiteLLMField
                  label="Max Tokens"
                  value={String(config.litellm.maxTokens)}
                  onChange={(value) =>
                    updateLiteLLMField('maxTokens', Number.parseInt(value || '0', 10) || 0)
                  }
                  type="number"
                />
              </div>
            </TabsContent>
            <TabsContent value="litellm" className="bottom-tab-content">
              <div className="config-grid two-column">
                <LiteLLMField
                  label="Model"
                  value={config.litellm.model}
                  onChange={(value) => updateLiteLLMField('model', value)}
                />
                <LiteLLMField
                  label="Temperature"
                  value={String(config.litellm.temperature)}
                  onChange={(value) =>
                    updateLiteLLMField('temperature', Number.parseFloat(value || '0') || 0)
                  }
                  type="number"
                />
                <LiteLLMField
                  label="Masked API Key"
                  value="****************"
                  onChange={() => {}}
                  type="password"
                />
              </div>
            </TabsContent>
          </Tabs>
        </section>
      </div>
    </TooltipProvider>
  )
}

interface McpServerEditorProps {
  index: number
  server: MCPServerConfig
  onModeChange: (index: number, mode: MCPMode) => void
  onUpdate: (
    index: number,
    patch: Partial<ScaffoldRequest['mcpServers'][number]>
  ) => void
}

function McpServerEditor({
  index,
  server,
  onModeChange,
  onUpdate,
}: McpServerEditorProps) {
  return (
    <article className="config-card">
      <label className="panel-field">
        <span>Server Name</span>
        <input
          type="text"
          value={server.name}
          onChange={(event) => onUpdate(index, { name: event.target.value })}
        />
      </label>
      <label className="panel-field">
        <span>Mode</span>
        <Select value={server.mode} onValueChange={(value) => onModeChange(index, value as MCPMode)}>
          <SelectTrigger className="mode-select">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="stdio">stdio</SelectItem>
            <SelectItem value="sse">sse</SelectItem>
            <SelectItem value="disabled">disabled</SelectItem>
          </SelectContent>
        </Select>
      </label>
      {server.mode === 'stdio' ? (
        <label className="panel-field">
          <span>Command</span>
          <input
            type="text"
            value={server.command ?? ''}
            onChange={(event) => onUpdate(index, { command: event.target.value })}
          />
        </label>
      ) : null}
      {server.mode === 'sse' ? (
        <label className="panel-field">
          <span>SSE URL</span>
          <input
            type="text"
            value={server.url ?? ''}
            onChange={(event) => onUpdate(index, { url: event.target.value })}
          />
        </label>
      ) : null}
    </article>
  )
}

interface LiteLLMFieldProps {
  label: string
  onChange: (value: string) => void
  type?: 'text' | 'number' | 'password'
  value: string
}

function LiteLLMField({
  label,
  onChange,
  type = 'text',
  value,
}: LiteLLMFieldProps) {
  return (
    <label className="panel-field">
      <span>{label}</span>
      <input type={type} value={value} onChange={(event) => onChange(event.target.value)} />
    </label>
  )
}

function createPreviewFiles(config: ScaffoldRequest): GeneratedFile[] {
  const deterministicTools = (config.rootAgent.subAgents ?? [])
    .flatMap((agent) => agent.tools ?? [])
    .filter((tool) => tool.isDeterministic)
    .map((tool) => tool.name)

  return [
    {
      filename: 'agent.py',
      content: [
        `PROJECT_NAME = "${config.projectName}"`,
        '',
        `ROOT_AGENT = "${config.rootAgent.name}"`,
        `SUB_AGENTS = [${(config.rootAgent.subAgents ?? [])
          .map((agent) => `"${agent.name}"`)
          .join(', ')}]`,
        '',
        ...deterministicTools.map((tool) => `${tool}()`),
      ].join('\n'),
    },
    {
      filename: 'LOAD_CONTEXT.md',
      content: [
        `# ${config.projectName}`,
        '',
        '## Agents',
        `- Root: ${config.rootAgent.name}`,
        ...(config.rootAgent.subAgents ?? []).map((agent) => `- Child: ${agent.name}`),
      ].join('\n'),
    },
    {
      filename: 'TODO.md',
      content: [
        `# TODO - ${config.projectName}`,
        '',
        '- Review generated topology',
        '- Validate deterministic tool boundaries',
        '- Wire backend integration in checkpoint 8',
      ].join('\n'),
    },
  ]
}

export default App
