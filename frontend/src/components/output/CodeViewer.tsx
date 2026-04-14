import { useEffect, useState } from 'react'
import { Copy, CopyCheck } from 'lucide-react'
import { atomOneLight } from 'react-syntax-highlighter/dist/esm/styles/hljs'
import { docco } from 'react-syntax-highlighter/dist/esm/styles/hljs'
import { LightAsync as SyntaxHighlighter } from 'react-syntax-highlighter'

import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import type { GeneratedFile } from '@/types'

interface CodeViewerProps {
  files: GeneratedFile[]
}

export function CodeViewer({ files }: CodeViewerProps) {
  const [activeFile, setActiveFile] = useState(files[0]?.filename ?? '')
  const [copiedFile, setCopiedFile] = useState<string | null>(null)

  useEffect(() => {
    setActiveFile(files[0]?.filename ?? '')
  }, [files])

  return (
    <Tabs
      className="code-viewer"
      value={activeFile}
      onValueChange={setActiveFile}
    >
      <TabsList className="code-viewer-tabs" variant="line">
        {files.map((file) => (
          <TabsTrigger key={file.filename} value={file.filename}>
            {file.filename}
          </TabsTrigger>
        ))}
      </TabsList>
      {files.map((file) => (
        <TabsContent key={file.filename} value={file.filename} className="code-viewer-panel">
          <div className="code-viewer-toolbar">
            <span className="code-viewer-filename">{file.filename}</span>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => void copyFile(file, setCopiedFile)}
            >
              {copiedFile === file.filename ? <CopyCheck size={14} /> : <Copy size={14} />}
              {copiedFile === file.filename ? 'Copied' : 'Copy'}
            </Button>
          </div>
          <SyntaxHighlighter
            customStyle={{ margin: 0, background: 'transparent' }}
            language={detectLanguage(file.filename)}
            style={file.filename.endsWith('.md') ? docco : atomOneLight}
            wrapLongLines
          >
            {file.content}
          </SyntaxHighlighter>
        </TabsContent>
      ))}
    </Tabs>
  )
}

function detectLanguage(filename: string): string {
  if (filename.endsWith('.py')) {
    return 'python'
  }
  if (filename.endsWith('.md')) {
    return 'markdown'
  }
  if (filename.endsWith('.txt') || filename.endsWith('.example')) {
    return 'bash'
  }
  return 'plaintext'
}

async function copyFile(
  file: GeneratedFile,
  setCopiedFile: (filename: string | null) => void
): Promise<void> {
  await navigator.clipboard.writeText(file.content)
  setCopiedFile(file.filename)
  window.setTimeout(() => setCopiedFile(null), 1500)
}
