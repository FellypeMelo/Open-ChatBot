import React, { memo } from 'react';

interface MessageRendererProps {
  content: string;
}

const MessageRenderer: React.FC<MessageRendererProps> = memo(({ content }) => {
  // Regex to split content into blocks of:
  // 1. Actions: **bold**
  // 2. Thoughts: *italic*
  // 3. Speech: everything else
  // Note: We use non-greedy matching to handle multiple occurrences
  // and we match ** before * to ensure precedence.
  const parts = content.split(/(\*\*.+?\*\*|\*.+?\*)/g);

  return (
    <div className="font-body-lg leading-relaxed whitespace-pre-wrap text-on-surface">
      {parts.map((part, i) => {
        // Match Action: **text**
        if (part.startsWith('**') && part.endsWith('**') && part.length > 4) {
          const inner = part.slice(2, -2);
          return (
            <span key={i} className="font-bold text-primary">
              {inner}
            </span>
          );
        }
        
        // Match Thought: *text*
        if (part.startsWith('*') && part.endsWith('*') && part.length > 2) {
          const inner = part.slice(1, -1);
          return (
            <span key={i} className="italic text-on-surface-variant/70">
              {inner}
            </span>
          );
        }
        
        // Default Speech - filter out empty strings from split
        if (!part) return null;
        return <span key={i}>{part}</span>;
      })}
    </div>
  );
});

export default MessageRenderer;
