import React, { memo } from 'react';

interface MessageRendererProps {
  content: string;
}

const MessageRenderer: React.FC<MessageRendererProps> = memo(({ content }) => {
  // Parse *text* into italicized <em> tags for actions/thoughts
  const parts = content.split(/(\*[^*]+\*)/g);

  return (
    <div className="font-body-lg leading-relaxed whitespace-pre-wrap">
      {parts.map((part, i) => {
        if (part.startsWith('*') && part.endsWith('*') && part.length > 1) {
          const inner = part.slice(1, -1);
          return <em key={i} className="text-on-surface-variant">{inner}</em>;
        }
        return <span key={i}>{part}</span>;
      })}
    </div>
  );
});

export default MessageRenderer;
