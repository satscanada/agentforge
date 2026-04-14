import type { AgentDefinition } from '@/types'

import { AgentTypeSelect } from './AgentTypeSelect'
import { ToolRow } from './ToolRow'

interface AgentCardProps {
  agent: AgentDefinition
  depth?: number
}

export function AgentCard({ agent, depth = 0 }: AgentCardProps) {
  const subAgents = agent.subAgents ?? []
  const tools = agent.tools ?? []

  return (
    <article className="agent-card" style={{ ['--depth' as string]: depth }}>
      <header className="agent-card-header">
        <div>
          <p className="agent-kicker">{depth === 0 ? 'Root Agent' : 'Sub-Agent'}</p>
          <h3>{agent.name}</h3>
        </div>
        <AgentTypeSelect value={agent.agentType} />
      </header>

      <p className="agent-instructions">{agent.instructions}</p>

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
            {subAgents.map((subAgent) => (
              <AgentCard key={subAgent.name} agent={subAgent} depth={depth + 1} />
            ))}
          </div>
        </section>
      ) : null}
    </article>
  )
}
