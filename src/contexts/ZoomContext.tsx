import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

interface ZoomContextType {
  zoomLevel: number;
  zoomIn: () => void;
  zoomOut: () => void;
  resetZoom: () => void;
  setZoomLevel: (level: number) => void;
}

const ZoomContext = createContext<ZoomContextType | undefined>(undefined);

const ZOOM_MIN = 0.5;  // 50%
const ZOOM_MAX = 2.0;  // 200%
const ZOOM_STEP = 0.1; // 10%
const ZOOM_DEFAULT = 1.0; // 100%
const STORAGE_KEY = 'opcode-zoom-level';

export const ZoomProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [zoomLevel, setZoomLevelState] = useState<number>(() => {
    // Load from localStorage on mount
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      const parsed = parseFloat(stored);
      if (!isNaN(parsed) && parsed >= ZOOM_MIN && parsed <= ZOOM_MAX) {
        return parsed;
      }
    }
    return ZOOM_DEFAULT;
  });

  // Persist to localStorage whenever zoom changes
  useEffect(() => {
    console.log('[ZoomContext] Zoom level changed to:', zoomLevel);
    localStorage.setItem(STORAGE_KEY, zoomLevel.toString());

    // Apply to CSS variable
    document.documentElement.style.setProperty('--conversation-zoom', zoomLevel.toString());
    console.log('[ZoomContext] CSS variable --conversation-zoom set to:', zoomLevel);
  }, [zoomLevel]);

  const setZoomLevel = useCallback((level: number) => {
    const clamped = Math.max(ZOOM_MIN, Math.min(ZOOM_MAX, level));
    const rounded = Math.round(clamped * 10) / 10; // Round to 1 decimal
    setZoomLevelState(rounded);
  }, []);

  const zoomIn = useCallback(() => {
    setZoomLevel(zoomLevel + ZOOM_STEP);
  }, [zoomLevel, setZoomLevel]);

  const zoomOut = useCallback(() => {
    setZoomLevel(zoomLevel - ZOOM_STEP);
  }, [zoomLevel, setZoomLevel]);

  const resetZoom = useCallback(() => {
    setZoomLevel(ZOOM_DEFAULT);
  }, [setZoomLevel]);

  return (
    <ZoomContext.Provider value={{ zoomLevel, zoomIn, zoomOut, resetZoom, setZoomLevel }}>
      {children}
    </ZoomContext.Provider>
  );
};

export const useZoom = () => {
  const context = useContext(ZoomContext);
  if (context === undefined) {
    throw new Error('useZoom must be used within a ZoomProvider');
  }
  return context;
};
