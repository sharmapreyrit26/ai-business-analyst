import {
  createContext,
  ReactNode,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react'

import {
  applyTheme,
  loadTheme,
  ThemeMode,
} from './theme'


type ThemeContextValue = {
  mode: ThemeMode

  setMode: (
    mode: ThemeMode
  ) => void

  toggleTheme: () => void
}


const ThemeContext =
  createContext<
    ThemeContextValue | undefined
  >(
    undefined
  )


type ThemeProviderProps = {
  children: ReactNode
}


export function ThemeProvider({
  children,
}: ThemeProviderProps) {
  const [
    mode,
    setModeState,
  ] = useState<ThemeMode>(
    () => loadTheme()
  )


  useEffect(
    () => {
      applyTheme(
        mode
      )
    },
    [
      mode,
    ]
  )


  useEffect(
    () => {
      if (
        mode
        !== 'system'
      ) {
        return
      }

      const media =
        window.matchMedia(
          '(prefers-color-scheme: dark)'
        )

      const handleChange = () => {
        applyTheme(
          'system'
        )
      }

      media.addEventListener(
        'change',
        handleChange
      )

      return () => {
        media.removeEventListener(
          'change',
          handleChange
        )
      }
    },
    [
      mode,
    ]
  )


  function setMode(
    nextMode: ThemeMode
  ) {
    setModeState(
      nextMode
    )
  }


  function toggleTheme() {
    setModeState(
      current => {
        if (
          current
          === 'dark'
        ) {
          return 'light'
        }

        return 'dark'
      }
    )
  }


  const value =
    useMemo(
      () => ({
        mode,
        setMode,
        toggleTheme,
      }),
      [
        mode,
      ]
    )


  return (
    <ThemeContext.Provider
      value={value}
    >
      {children}
    </ThemeContext.Provider>
  )
}


export function useTheme() {
  const context =
    useContext(
      ThemeContext
    )

  if (!context) {
    throw new Error(
      'useTheme must be used inside ThemeProvider.'
    )
  }

  return context
}
