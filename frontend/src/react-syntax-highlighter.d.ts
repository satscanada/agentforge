declare module 'react-syntax-highlighter' {
  import { ComponentType, CSSProperties, ReactNode } from 'react'

  export interface SyntaxHighlighterProps {
    children?: ReactNode
    language?: string
    style?: Record<string, CSSProperties>
    customStyle?: CSSProperties
    wrapLongLines?: boolean
  }

  export const LightAsync: ComponentType<SyntaxHighlighterProps>
}

declare module 'react-syntax-highlighter/dist/esm/styles/hljs' {
  import { CSSProperties } from 'react'

  export const atomOneLight: Record<string, CSSProperties>
  export const docco: Record<string, CSSProperties>
}
