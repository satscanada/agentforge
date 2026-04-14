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
  disabled?: boolean
  onValueChange?: (value: AgentType) => void
}

export function AgentTypeSelect({
  value,
  disabled = false,
  onValueChange,
}: AgentTypeSelectProps) {
  return (
    <Select
      defaultValue={value}
      value={value}
      disabled={disabled}
      onValueChange={(nextValue) => {
        if (nextValue !== null) {
          onValueChange?.(nextValue)
        }
      }}
    >
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
