import {
  startTransition,
  useDeferredValue,
  useEffect,
  useEffectEvent,
  useState,
} from 'react'
import type { CSSProperties } from 'react'
import { Eye, LockKeyhole, LockKeyholeOpen } from 'lucide-react'

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
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'
import { useAgentConfigStore } from '@/store/agentConfig'
import { checkHealth, downloadZip, generateProject, runLiveTest } from '@/api/scaffold'
import type {
  GeneratedFile,
  MCPServerConfig,
  MCPMode,
  ScaffoldRequest,
  TestRunResponse,
} from '@/types'

const HEALTH_POLL_INTERVAL_MS = 30_000

function App() {
  const config = useAgentConfigStore((state) => state.config)
  const resetConfig = useAgentConfigStore((state) => state.resetConfig)
  const loadBootstrapExample = useAgentConfigStore(
    (state) => state.loadBootstrapExample
  )
  const setProjectName = useAgentConfigStore((state) => state.setProjectName)
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
  const [isHealthy, setIsHealthy] = useState(false)
  const [isPreviewOpen, setIsPreviewOpen] = useState(false)
  const [isTopologyLocked, setIsTopologyLocked] = useState(true)
  const [testPrompt, setTestPrompt] = useState(
    'Create a quick test run for this topology and explain which agent handles what.'
  )
  const [isRunningTest, setIsRunningTest] = useState(false)
  const [testRun, setTestRun] = useState<TestRunResponse | null>(null)
  const [testError, setTestError] = useState<string | null>(null)

  const pollHealth = useEffectEvent(async () => {
    try {
      const nextHealth = await checkHealth()
      setIsHealthy(nextHealth.status === 'ok')
    } catch {
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
      setGeneratedFiles(createPreviewFiles(deferredConfig))
    })
  }, [deferredConfig, downloadToken])

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

  const handleRunLiveTest = async () => {
    setIsRunningTest(true)
    setTestError(null)
    try {
      const response = await runLiveTest(config, testPrompt)
      startTransition(() => {
        setTestRun(response)
      })
    } catch (error) {
      const message =
        error instanceof Error ? error.message : 'Live test runner failed to execute.'
      setTestError(message)
    } finally {
      setIsRunningTest(false)
    }
  }

  const handleDownload = () => {
    if (downloadToken !== null) {
      downloadZip(downloadToken)
    }
  }

  const handleReset = () => {
    resetConfig()
    setIsTopologyLocked(true)
    setDownloadToken(null)
  }

  const handleLoadBootstrap = () => {
    loadBootstrapExample()
    setIsTopologyLocked(true)
    setDownloadToken(null)
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
            <div className="header-meta">
              <div className="health-pill">
                <span className="sr-only">
                  {isHealthy ? 'Backend healthy' : 'Backend offline'}
                </span>
                <span className={`health-dot ${isHealthy ? 'is-online' : 'is-offline'}`} />
              </div>
              <label className="project-name-field">
                <span>Project Name</span>
                <input
                  type="text"
                  value={config.projectName}
                  onChange={(event) => setProjectName(event.target.value)}
                />
              </label>
            </div>
            <div className="header-actions">
              <Button onClick={handleReset} type="button" variant="outline">
                Reset Project
              </Button>
              <Button onClick={handleLoadBootstrap} type="button" variant="outline">
                Load CD Ladder
              </Button>
              <Button onClick={() => void handleGenerate()} type="button">
                {isGenerating ? 'Generating...' : 'Generate'}
              </Button>
              <DownloadButton disabled={downloadToken === null} onClick={handleDownload} />
            </div>
          </div>
        </header>

        <main className="workspace-grid">
          <section className="workspace-panel topology-panel">
            <div className="panel-heading panel-heading-row">
              <div>
                <p className="eyebrow">Topology</p>
                <h2>{formatTopologyTitle(config.projectName)}</h2>
              </div>
              <div className="topology-actions">
                <Button
                  onClick={() => setIsPreviewOpen(true)}
                  size="sm"
                  type="button"
                  variant="outline"
                >
                  <Eye size={14} />
                  Preview JSON
                </Button>
                <Tooltip>
                  <TooltipTrigger render={<span />}>
                    <Button
                      aria-label={
                        isTopologyLocked
                          ? 'Unlock topology editing'
                          : 'Lock topology editing'
                      }
                      className="topology-lock-button"
                      onClick={() => setIsTopologyLocked((current) => !current)}
                      size="icon-sm"
                      type="button"
                      variant={isTopologyLocked ? 'outline' : 'default'}
                    >
                      {isTopologyLocked ? <LockKeyhole size={14} /> : <LockKeyholeOpen size={14} />}
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    {isTopologyLocked
                      ? 'Topology is locked. Unlock to edit agent names, types, and instructions.'
                      : 'Topology is unlocked. Lock it again to prevent accidental changes.'}
                  </TooltipContent>
                </Tooltip>
              </div>
            </div>
            <AgentCard agent={deferredConfig.rootAgent} locked={isTopologyLocked} />
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
              <TabsTrigger value="test">Live Test</TabsTrigger>
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
            <TabsContent value="test" className="bottom-tab-content">
              <div className="test-runner-shell">
                <article className="test-runner-card">
                  <div className="panel-heading">
                    <p className="eyebrow">Runner Input</p>
                    <h2>Live Agent Test Runner</h2>
                  </div>
                  <label className="panel-field">
                    <span>Test Prompt</span>
                    <textarea
                      className="test-runner-input"
                      onChange={(event) => setTestPrompt(event.target.value)}
                      placeholder="Describe the scenario you want to simulate."
                      value={testPrompt}
                    />
                  </label>
                  <div className="test-runner-toolbar">
                    <Button onClick={() => void handleRunLiveTest()} type="button">
                      {isRunningTest ? 'Running Test...' : 'Run Live Test'}
                    </Button>
                    <p>
                      Runs a backend simulation against the current topology, tools, session, and
                      MCP setup.
                    </p>
                  </div>
                  {testError ? <p className="test-runner-error">{testError}</p> : null}
                </article>

                <article className="test-runner-card">
                  <div className="panel-heading">
                    <p className="eyebrow">Runner Output</p>
                    <h2>Execution Trace</h2>
                  </div>
                  {testRun ? (
                    <div className="test-runner-results">
                      <div className="test-runner-summary">
                        <p className="section-label">Final Output</p>
                        <pre className="test-runner-final-output">
                          <code>{testRun.finalOutput}</code>
                        </pre>
                      </div>
                      {testRun.warnings.length > 0 ? (
                        <div className="test-runner-warnings">
                          <p className="section-label">Warnings</p>
                          {testRun.warnings.map((warning) => (
                            <p key={warning} className="test-runner-warning">
                              {warning}
                            </p>
                          ))}
                        </div>
                      ) : null}
                      <div className="test-runner-trace">
                        {testRun.steps.map((step, index) => (
                          <article
                            key={`${step.agentName}-${index}`}
                            className="test-run-step"
                            style={{ '--depth': step.depth } as CSSProperties}
                          >
                            <div className="test-run-step-header">
                              <div>
                                <p className="agent-kicker">
                                  {step.mode} · {step.agentType}
                                </p>
                                <h3>{step.agentName}</h3>
                              </div>
                              <span className="test-run-step-index">Step {index + 1}</span>
                            </div>
                            <p>{step.summary}</p>
                            {step.toolsUsed.length > 0 ? (
                              <p className="test-run-tools">
                                Tools: {step.toolsUsed.join(', ')}
                              </p>
                            ) : null}
                            <pre className="test-run-step-output">
                              <code>{step.output}</code>
                            </pre>
                          </article>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div className="test-runner-empty">
                      <p>Run a prompt to inspect how the current topology behaves.</p>
                    </div>
                  )}
                </article>
              </div>
            </TabsContent>
          </Tabs>
        </section>

        {isPreviewOpen ? (
          <div
            className="preview-modal-backdrop"
            onClick={() => setIsPreviewOpen(false)}
            role="presentation"
          >
            <section
              aria-label="State Preview"
              aria-modal="true"
              className="preview-modal"
              onClick={(event) => event.stopPropagation()}
              role="dialog"
            >
              <div className="panel-heading panel-heading-row">
                <div>
                  <p className="eyebrow">State Preview</p>
                  <h2>Live Zustand JSON</h2>
                </div>
                <Button
                  onClick={() => setIsPreviewOpen(false)}
                  type="button"
                  variant="outline"
                >
                  Close
                </Button>
              </div>
              <pre className="json-preview modal-json-preview">
                <code>{JSON.stringify(deferredConfig, null, 2)}</code>
              </pre>
            </section>
          </div>
        ) : null}
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

function formatTopologyTitle(projectName: string): string {
  return projectName
    .split(/[-_\s]+/)
    .filter(Boolean)
    .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
    .join(' ') || 'Agent Topology'
}

export default App
