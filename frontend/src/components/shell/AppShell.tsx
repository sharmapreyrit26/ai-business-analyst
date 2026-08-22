import {
  ReactNode,
} from 'react'

import {
  NewSidebar,
} from './NewSidebar'

import {
  NewHeader,
} from './NewHeader'


type AppShellProps = {
  children: ReactNode
}


export function AppShell({
  children,
}: AppShellProps) {
  return (
    <div className="pl-shell">

      <NewSidebar />

      <div className="pl-shell-main">

        <NewHeader />

        <main className="pl-content">
          {children}
        </main>

      </div>

    </div>
  )
}
