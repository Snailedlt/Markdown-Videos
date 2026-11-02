import '@testing-library/jest-dom/vitest'

// jsdom doesn't implement matchMedia; the generator uses it to decide whether
// to focus the link box (not on touch screens).
if (!window.matchMedia) {
  window.matchMedia = (query: string) =>
    ({
      matches: false,
      media: query,
      onchange: null,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => false,
    }) as MediaQueryList
}
