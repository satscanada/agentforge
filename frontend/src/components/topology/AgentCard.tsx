import type { AgentDefinition } from '@/types'
import { useAgentConfigStore } from '@/store/agentConfig'

import { AgentTypeSelect } from './AgentTypeSelect'
import { ToolRow } from './ToolRow'

interface AgentCardProps {
  agent: AgentDefinition
  depth?: number
  path?: number[]
  locked?: boolean
}

export function AgentCard({
  agent,
  depth = 0,
  path = [],
  locked = true,
}: AgentCardProps) {
  const updateAgentField = useAgentConfigStore((state) => state.updateAgentField)
  const setAgentType = useAgentConfigStore((state) => state.setAgentType)
  const addSubAgent = useAgentConfigStore((state) => state.addSubAgent)
  const subAgents = agent.subAgents ?? []
  const tools = agent.tools ?? []
  const canHaveSubAgents = agent.agentType !== 'llm'

  return (
    <article className="agent-card" style={{ ['--depth' as string]: depth }}>
      <header className="agent-card-header">
        <div className="agent-card-title">
          <p className="agent-kicker">{depth === 0 ? 'Root Agent' : 'Sub-Agent'}</p>
          <input
            aria-label={`${depth === 0 ? 'Root agent' : 'Sub-agent'} name`}
            className="agent-name-input"
            disabled={locked}
            onChange={(event) => updateAgentField(path, 'name', event.target.value)}
            type="text"
            value={agent.name}
          />
        </div>
        <AgentTypeSelect
          disabled={locked}
          onValueChange={(value) => setAgentType(path, value)}
          value={agent.agentType}
        />
      </header>

      <label className="panel-field agent-field">
        <span>Instructions</span>
        <textarea
          className="agent-instructions-input"
          disabled={locked}
          onChange={(event) => updateAgentField(path, 'instructions', event.target.value)}
          rows={3}
          value={agent.instructions}
        />
      </label>

      {tools.length > 0 ? (
        <section className="agent-tools">
          <p className="section-label">Tools</p>
          <div className="agent-tools-list">
            {tools.map((tool) => (
              <ToolRow key={tool.name} tool={tool} />
            ))}
          </div>
        </section>
      ) : null}

      {subAgents.length > 0 ? (
        <section className="agent-children">
          <p className="section-label">Sub-Agents</p>
          <div className="agent-children-list">
            {subAgents.map((subAgent, index) => (
              <AgentCard
                key={`${subAgent.name}-${index}`}
                agent={subAgent}
                depth={depth + 1}
                locked={locked}
                path={[...path, index]}
              />
            ))}
          </div>
        </section>
      ) : null}

      {!locked && canHaveSubAgents ? (
        <button
          className="add-sub-agent-btn"
          onClick={() => addSubAgent(path)}
          type="button"
        >
          + Add Sub-Agent
        </button>
      ) : null}
    </article>
  )
}
