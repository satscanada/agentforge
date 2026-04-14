import { Download } from 'lucide-react'

import { Button } from '@/components/ui/button'

interface DownloadButtonProps {
  disabled?: boolean
  onClick: () => void
}

export function DownloadButton({ disabled = false, onClick }: DownloadButtonProps) {
  return (
    <Button disabled={disabled} onClick={onClick} type="button" variant="outline">
      <Download size={14} />
      Download ZIP
    </Button>
  )
}
