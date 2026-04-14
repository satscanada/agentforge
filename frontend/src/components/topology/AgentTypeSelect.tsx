import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import type { AgentType } from '@/types'

const AGENT_TYPES: AgentType[] = ['llm', 'sequential', 'parallel', 'loop']

interface AgentTypeSelectProps {
  value: AgentType
}

export function AgentTypeSelect({ value }: AgentTypeSelectProps) {
  return (
    <Select defaultValue={value} value={value} disabled>
      <SelectTrigger className="agent-type-select" size="sm">
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        {AGENT_TYPES.map((agentType) => (
          <SelectItem key={agentType} value={agentType}>
            {agentType}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}
