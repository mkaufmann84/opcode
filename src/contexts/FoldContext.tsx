import React, { createContext, useContext, useState, useCallback } from 'react';

interface FoldContextType {
  foldedIds: Set<string>;
  foldAll: () => void;
  unfoldAll: () => void;
  toggleFold: (id: string) => void;
  isFolded: (id: string) => boolean;
  setFolded: (id: string, folded: boolean) => void;
  expandedMessageIds: Set<string>;
  toggleMessageExpand: (id: string) => void;
  isMessageExpanded: (id: string) => boolean;
}

const FoldContext = createContext<FoldContextType | undefined>(undefined);

export const FoldProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [foldedIds, setFoldedIds] = useState<Set<string>>(new Set());
  const [expandedMessageIds, setExpandedMessageIds] = useState<Set<string>>(new Set());

  const foldAll = useCallback(() => {
    console.log('[FoldContext] Folding all');
    // We'll set a flag that child components can check
    // For now, we'll use a special ID to indicate "all folded" state
    setFoldedIds(new Set(['__ALL_FOLDED__']));
  }, []);

  const unfoldAll = useCallback(() => {
    console.log('[FoldContext] Unfolding all');
    // Clear everything including expand overrides
    setFoldedIds(new Set());
  }, []);

  const toggleFold = useCallback((id: string) => {
    setFoldedIds(prev => {
      const next = new Set(prev);

      // If global fold is active, toggle expand override
      if (prev.has('__ALL_FOLDED__')) {
        const expandKey = `expand-${id}`;
        if (next.has(expandKey)) {
          next.delete(expandKey); // Collapse it again
        } else {
          next.add(expandKey); // Expand override
        }
        return next;
      }

      // Normal toggle when not in global fold mode
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }, []);

  const isFolded = useCallback((id: string) => {
    // Check if user explicitly expanded this widget during global fold
    if (foldedIds.has(`expand-${id}`)) {
      return false; // Override global fold for this specific widget
    }
    // If "all folded" flag is set, everything is folded
    if (foldedIds.has('__ALL_FOLDED__')) {
      return true;
    }
    return foldedIds.has(id);
  }, [foldedIds]);

  const setFolded = useCallback((id: string, folded: boolean) => {
    setFoldedIds(prev => {
      const next = new Set(prev);
      // Remove the "all folded" flag when manually setting
      next.delete('__ALL_FOLDED__');

      if (folded) {
        next.add(id);
      } else {
        next.delete(id);
      }
      return next;
    });
  }, []);

  const toggleMessageExpand = useCallback((id: string) => {
    setExpandedMessageIds(prev => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }, []);

  const isMessageExpanded = useCallback((id: string) => {
    return expandedMessageIds.has(id);
  }, [expandedMessageIds]);

  return (
    <FoldContext.Provider value={{
      foldedIds,
      foldAll,
      unfoldAll,
      toggleFold,
      isFolded,
      setFolded,
      expandedMessageIds,
      toggleMessageExpand,
      isMessageExpanded
    }}>
      {children}
    </FoldContext.Provider>
  );
};

export const useFold = () => {
  const context = useContext(FoldContext);
  if (context === undefined) {
    throw new Error('useFold must be used within a FoldProvider');
  }
  return context;
};
