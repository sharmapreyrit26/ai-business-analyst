export type ThemeMode =
  | 'light'
  | 'dark'
  | 'system'

export const THEME_STORAGE_KEY =
  'profitlens-theme'

export function resolveTheme(
  mode: ThemeMode
): 'light' | 'dark' {
  if (mode === 'light') {
    return 'light'
  }

  if (mode === 'dark') {
    return 'dark'
  }

  if (
    typeof window !== 'undefined'
    && window.matchMedia(
      '(prefers-color-scheme: dark)'
    ).matches
  ) {
    return 'dark'
  }

  return 'light'
}

export function applyTheme(
  mode: ThemeMode
) {
  const resolved =
    resolveTheme(
      mode
    )

  document.documentElement
    .setAttribute(
      'data-theme',
      resolved
    )

  localStorage.setItem(
    THEME_STORAGE_KEY,
    mode
  )
}

export function loadTheme():
  ThemeMode {
  const saved =
    localStorage.getItem(
      THEME_STORAGE_KEY
    )

  if (
    saved === 'light'
    || saved === 'dark'
    || saved === 'system'
  ) {
    return saved
  }

  return 'system'
}
