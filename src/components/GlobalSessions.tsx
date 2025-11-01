import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Terminal, Loader2, AlertCircle, Clock, FolderOpen } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api, type GlobalSession } from "@/lib/api";
import { cn } from "@/lib/utils";

interface GlobalSessionsProps {
  className?: string;
  onSessionClick?: (session: GlobalSession) => void;
}

/**
 * Component to display all active Claude sessions tracked by global hooks
 */
export function GlobalSessions({ className, onSessionClick }: GlobalSessionsProps) {
  const [sessions, setSessions] = useState<GlobalSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSessions();

    // Poll for updates every 3 seconds
    const interval = setInterval(loadSessions, 3000);
    return () => clearInterval(interval);
  }, []);

  const loadSessions = async () => {
    try {
      const data = await api.listGlobalSessions();
      setSessions(data);
      setError(null);
    } catch (err) {
      console.error("Failed to load global sessions:", err);
      setError("Failed to load sessions");
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "running":
        return <Badge variant="default" className="bg-green-600">🟢 Running</Badge>;
      case "waiting_for_input":
        return <Badge variant="secondary" className="bg-yellow-600">🟡 Waiting</Badge>;
      case "needs_permission":
        return <Badge variant="destructive" className="bg-red-600">🔴 Needs Permission</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const formatTimestamp = (timestamp: number) => {
    const date = new Date(timestamp * 1000);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return "just now";
    if (diffMins < 60) return `${diffMins}m ago`;

    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;

    return date.toLocaleDateString();
  };

  const getProjectName = (cwd: string) => {
    const parts = cwd.split("/");
    return parts[parts.length - 1] || cwd;
  };

  if (loading && sessions.length === 0) {
    return (
      <div className={cn("flex items-center justify-center py-8", className)}>
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (error) {
    return (
      <div className={cn("flex items-center gap-2 text-destructive py-4", className)}>
        <AlertCircle className="h-5 w-5" />
        <span>{error}</span>
      </div>
    );
  }

  if (sessions.length === 0) {
    return (
      <div className={cn("text-center py-12 text-muted-foreground", className)}>
        <Terminal className="h-12 w-12 mx-auto mb-4 opacity-50" />
        <p>No active Claude sessions</p>
        <p className="text-sm mt-2">Start a Claude session to see it here</p>
      </div>
    );
  }

  return (
    <div className={cn("space-y-4", className)}>
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">All Active Conversations</h2>
        <Badge variant="secondary">{sessions.length} active</Badge>
      </div>

      <div className="grid gap-3">
        {sessions.map((session) => (
          <motion.div
            key={session.session_id}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2 }}
          >
            <Card
              className={cn(
                "hover:shadow-md transition-all",
                onSessionClick && "cursor-pointer hover:border-primary/50"
              )}
              onClick={() => onSessionClick?.(session)}
            >
              <CardContent className="p-4">
                <div className="space-y-3">
                  {/* Header with status */}
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-2 flex-1 min-w-0">
                      <Terminal className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="font-mono text-xs text-muted-foreground truncate">
                          {session.session_id.substring(0, 24)}...
                        </p>
                      </div>
                    </div>
                    {getStatusBadge(session.status)}
                  </div>

                  {/* Project info */}
                  <div className="flex items-center gap-2 text-sm">
                    <FolderOpen className="h-4 w-4 text-muted-foreground" />
                    <span className="font-medium">{getProjectName(session.cwd)}</span>
                    <span className="text-muted-foreground text-xs truncate">
                      {session.cwd}
                    </span>
                  </div>

                  {/* Timing info */}
                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      <span>Started {formatTimestamp(session.started_at)}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <span>Last activity {formatTimestamp(session.last_activity)}</span>
                    </div>
                  </div>

                  {/* Last notification */}
                  {session.last_notification && (
                    <div className="text-xs text-muted-foreground bg-muted/50 rounded p-2">
                      💬 {session.last_notification}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
