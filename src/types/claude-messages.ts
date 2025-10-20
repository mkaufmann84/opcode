/**
 * Type definitions for Claude Code streaming messages with subagent support
 */

export type MessageType = "system" | "assistant" | "user" | "result" | "summary" | "file-history-snapshot";
export type MessageRole = "user" | "assistant";

// Content Types
export interface TextContent {
  type: "text";
  text?: string;
  [key: string]: any;
}

export interface ThinkingContent {
  type: "thinking";
  thinking?: string;
  signature?: string;
  [key: string]: any;
}

export interface ToolUseContent {
  type: "tool_use";
  id?: string;
  name?: string;
  input?: Record<string, any>;
  [key: string]: any;
}

export interface ToolResultContent {
  type: "tool_result";
  tool_use_id?: string;
  content?: string | any;
  is_error?: boolean;
  [key: string]: any;
}

export type MessageContent = TextContent | ThinkingContent | ToolUseContent | ToolResultContent;

// Usage Tracking
export interface TokenUsage {
  input_tokens: number;
  output_tokens: number;
  cache_creation_input_tokens?: number;
  cache_read_input_tokens?: number;
  cache_creation?: {
    ephemeral_5m_input_tokens?: number;
    ephemeral_1h_input_tokens?: number;
  };
  service_tier?: string;
}

// Message Envelope
export interface MessageEnvelope {
  role?: MessageRole;
  content?: MessageContent[] | string | any;
  model?: string;
  id?: string;
  type?: string;
  stop_reason?: string | null;
  stop_sequence?: string | null;
  usage?: TokenUsage;
  [key: string]: any;
}

// Thread Metadata - identifies main thread vs subagent messages
export interface ThreadMetadata {
  isSidechain?: boolean;
  parentUuid?: string | null;
  uuid?: string;
}

// Tool Result Metadata
export interface ToolUseResult {
  status?: "completed" | "failed" | "running";
  prompt?: string;
  content?: any;
  totalDurationMs?: number;
  totalTokens?: number;
  totalToolUseCount?: number;
  usage?: TokenUsage;
  filenames?: string[];
  durationMs?: number;
  numFiles?: number;
  truncated?: boolean;
}

// Session Context
export interface SessionContext {
  cwd?: string;
  sessionId?: string;
  version?: string;
  gitBranch?: string;
  userType?: "external" | "internal";
  requestId?: string;
  timestamp?: string;
}

// Specific Message Types
export interface SystemInitMessage extends SessionContext, ThreadMetadata {
  type: "system";
  subtype: "init";
  session_id: string;
  model: string;
  tools?: string[];
  [key: string]: any;
}

export interface SystemReminderMessage {
  type: "system";
  subtype?: string;
  message?: string;
  result?: string;
  [key: string]: any;
}

export interface SummaryMessage {
  type: "summary";
  summary: string;
  leafUuid: string;
  [key: string]: any;
}

export interface FileHistorySnapshotMessage {
  type: "file-history-snapshot";
  messageId: string;
  snapshot: {
    messageId: string;
    trackedFileBackups: Record<string, any>;
    timestamp: string;
  };
  isSnapshotUpdate: boolean;
  [key: string]: any;
}

export interface UserMessage extends SessionContext, ThreadMetadata {
  type: "user";
  message?: MessageEnvelope;
  thinkingMetadata?: {
    level?: string;
    disabled?: boolean;
    triggers?: string[];
  };
  toolUseResult?: ToolUseResult;
  isMeta?: boolean;
  [key: string]: any;
}

export interface AssistantMessage extends SessionContext, ThreadMetadata {
  type: "assistant";
  message?: MessageEnvelope;
  usage?: TokenUsage;
  [key: string]: any;
}

export interface ResultMessage {
  type: "result";
  subtype?: string;
  result?: any;
  error?: string;
  is_error?: boolean;
  duration_ms?: number;
  num_turns?: number;
  cost_usd?: number;
  total_cost_usd?: number;
  usage?: TokenUsage;
  [key: string]: any;
}

// Main Union Type
export type ClaudeStreamMessage =
  | SystemInitMessage
  | SystemReminderMessage
  | SummaryMessage
  | FileHistorySnapshotMessage
  | UserMessage
  | AssistantMessage
  | ResultMessage;

// Type Guards
export function isSystemInitMessage(msg: ClaudeStreamMessage): msg is SystemInitMessage {
  return msg.type === "system" && (msg as any).subtype === "init";
}

export function isSystemReminderMessage(msg: ClaudeStreamMessage): msg is SystemReminderMessage {
  return msg.type === "system" && (msg as any).subtype === "reminder";
}

export function isSummaryMessage(msg: ClaudeStreamMessage): msg is SummaryMessage {
  return msg.type === "summary";
}

export function isFileHistorySnapshot(msg: ClaudeStreamMessage): msg is FileHistorySnapshotMessage {
  return msg.type === "file-history-snapshot";
}

export function isUserMessage(msg: ClaudeStreamMessage): msg is UserMessage {
  return msg.type === "user";
}

export function isAssistantMessage(msg: ClaudeStreamMessage): msg is AssistantMessage {
  return msg.type === "assistant";
}

export function isResultMessage(msg: ClaudeStreamMessage): msg is ResultMessage {
  return msg.type === "result";
}

export function isSubagentMessage(msg: ClaudeStreamMessage): boolean {
  return "isSidechain" in msg && msg.isSidechain === true;
}

export function isRootMessage(msg: ClaudeStreamMessage): boolean {
  return "parentUuid" in msg && msg.parentUuid === null;
}

export function containsTaskToolUse(msg: ClaudeStreamMessage): boolean {
  if (!isAssistantMessage(msg)) return false;
  const content = msg.message?.content;
  if (!Array.isArray(content)) return false;
  return content.some((c: any) => c.type === "tool_use" && c.name?.toLowerCase() === "task");
}

export function extractTaskToolUse(msg: ClaudeStreamMessage): ToolUseContent | null {
  if (!isAssistantMessage(msg)) return null;
  const content = msg.message?.content;
  if (!Array.isArray(content)) return null;
  const taskTool = content.find((c: any) => c.type === "tool_use" && c.name?.toLowerCase() === "task");
  return taskTool && taskTool.type === "tool_use" ? taskTool as ToolUseContent : null;
}

// Message Relationship Helpers
export function buildMessageMap(messages: ClaudeStreamMessage[]): Map<string, ClaudeStreamMessage> {
  const map = new Map<string, ClaudeStreamMessage>();
  messages.forEach((msg) => {
    if ("uuid" in msg && msg.uuid) {
      map.set(msg.uuid, msg);
    }
  });
  return map;
}

export function getChildMessages(
  parentUuid: string,
  messages: ClaudeStreamMessage[]
): ClaudeStreamMessage[] {
  return messages.filter((msg) => "parentUuid" in msg && msg.parentUuid === parentUuid);
}

export function getParentMessage(
  msg: ClaudeStreamMessage,
  messageMap: Map<string, ClaudeStreamMessage>
): ClaudeStreamMessage | null {
  if (!("parentUuid" in msg) || !msg.parentUuid) return null;
  return messageMap.get(msg.parentUuid) || null;
}

export interface MessageThread {
  message: ClaudeStreamMessage;
  children: MessageThread[];
}

export function buildMessageThread(
  rootMessage: ClaudeStreamMessage,
  allMessages: ClaudeStreamMessage[]
): MessageThread {
  const uuid = "uuid" in rootMessage ? rootMessage.uuid : null;
  if (!uuid) {
    return { message: rootMessage, children: [] };
  }
  const children = getChildMessages(uuid, allMessages);
  return {
    message: rootMessage,
    children: children.map((child) => buildMessageThread(child, allMessages)),
  };
}

export interface MessageGroups {
  mainThread: ClaudeStreamMessage[];
  subagentThreads: Map<string, ClaudeStreamMessage[]>;
}

export function groupMessagesByThread(messages: ClaudeStreamMessage[]): MessageGroups {
  const mainThread: ClaudeStreamMessage[] = [];
  const subagentThreads = new Map<string, ClaudeStreamMessage[]>();
  const messageMap = buildMessageMap(messages);

  messages.forEach((msg) => {
    if (isSubagentMessage(msg)) {
      if (isRootMessage(msg)) {
        const uuid = "uuid" in msg ? msg.uuid : null;
        if (uuid) {
          subagentThreads.set(uuid, [msg]);
        }
      } else {
        let current = msg;
        let rootUuid: string | null = null;

        while ("parentUuid" in current && current.parentUuid) {
          const parent = messageMap.get(current.parentUuid);
          if (!parent) break;
          if (isRootMessage(parent)) {
            rootUuid = "uuid" in parent ? parent.uuid : null;
            break;
          }
          current = parent;
        }

        if (rootUuid) {
          const thread = subagentThreads.get(rootUuid) || [];
          thread.push(msg);
          subagentThreads.set(rootUuid, thread);
        }
      }
    } else {
      mainThread.push(msg);
    }
  });

  return { mainThread, subagentThreads };
}

export interface TaskToSubagentLink {
  taskToolUseId: string;
  taskMessage: ClaudeStreamMessage;
  subagentRootUuid: string | null;
  subagentMessages: ClaudeStreamMessage[];
}

export function linkTasksToSubagents(messages: ClaudeStreamMessage[]): TaskToSubagentLink[] {
  const links: TaskToSubagentLink[] = [];

  messages.forEach((msg) => {
    const taskTool = extractTaskToolUse(msg);
    if (!taskTool) return;

    const msgUuid = "uuid" in msg ? msg.uuid : null;
    if (!msgUuid) return;

    const subagentRoot = messages.find((m) => {
      return (
        isSubagentMessage(m) &&
        isRootMessage(m) &&
        isUserMessage(m) &&
        "timestamp" in m &&
        "timestamp" in msg &&
        m.timestamp && msg.timestamp &&
        new Date(m.timestamp).getTime() >= new Date(msg.timestamp).getTime()
      );
    });

    if (subagentRoot && "uuid" in subagentRoot && subagentRoot.uuid) {
      const subagentMessages = getChildMessages(subagentRoot.uuid, messages);
      subagentMessages.unshift(subagentRoot);

      links.push({
        taskToolUseId: taskTool.id || "",
        taskMessage: msg,
        subagentRootUuid: subagentRoot.uuid,
        subagentMessages,
      });
    } else {
      links.push({
        taskToolUseId: taskTool.id || "",
        taskMessage: msg,
        subagentRootUuid: null,
        subagentMessages: [],
      });
    }
  });

  return links;
}
