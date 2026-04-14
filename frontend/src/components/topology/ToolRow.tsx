import { LockKeyhole } from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/components/ui/tooltip'
import type { ToolDefinition } from '@/types'

interface ToolRowProps {
  tool: ToolDefinition
}

export function ToolRow({ tool }: ToolRowProps) {
  return (
    <div className="tool-row">
      <div>
        <div className="tool-name-wrap">
          <span className="tool-name">{tool.name}</span>
          {tool.isDeterministic ? (
            <Tooltip>
              <TooltipTrigger>
                <Badge className="tool-badge" variant="secondary">
                  <LockKeyhole size={12} />
                  Deterministic
                </Badge>
              </TooltipTrigger>
              <TooltipContent>
                Direct Python call. This tool should not be routed through the LLM.
              </TooltipContent>
            </Tooltip>
          ) : null}
        </div>
        <p className="tool-description">{tool.description}</p>
      </div>
    </div>
  )
}
