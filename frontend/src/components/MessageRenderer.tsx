import React from 'react';

export interface SequenceBlock {
  type: 'thought' | 'action' | 'speech';
  content: string;
}

interface MessageRendererProps {
  sequence?: SequenceBlock[];
  fallback?: {
    content: string;
    thought?: string;
    actions?: string[];
  };
}

const MessageRenderer: React.FC<MessageRendererProps> = ({ sequence, fallback }) => {
  if (sequence && sequence.length > 0) {
    return (
      <div className="message-container leading-relaxed">
        {sequence.map((block, i) => (
          <span 
            key={i} 
            className={
              block.type === 'thought' ? 'italic text-zinc-400 text-[0.95em]' : 
              block.type === 'action' ? 'font-bold text-zinc-300' : 
              'text-zinc-100'
            }
          >
            {block.content}
            {" "}
          </span>
        ))}
      </div>
    );
  }

  // Fallback for non-sequence messages
  return (
    <div className="flex flex-col gap-1.5 w-full">
      {fallback?.actions && fallback.actions.length > 0 && (
        <div className="px-2 text-xs font-bold text-emerald-500/80 uppercase tracking-widest">
          {fallback.actions.map(a => `**${a}**`).join(' ')}
        </div>
      )}
      <div className="p-4 rounded-2xl shadow-lg border bg-zinc-900 border-zinc-800 text-zinc-100 rounded-tl-none">
        {fallback?.thought && (
          <div className="text-sm italic text-zinc-400 mb-2 border-l-2 border-emerald-500/30 pl-3 py-0.5">
            {fallback.thought}
          </div>
        )}
        <p className="whitespace-pre-wrap leading-relaxed">
          {fallback?.content}
        </p>
      </div>
    </div>
  );
};

export default MessageRenderer;
