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
      <div className="message-container leading-relaxed spatial-field p-8 rounded-3xl transition-all duration-500 hover:scale-[1.01]">
        {sequence.map((block, i) => {
          let className = 'text-zinc-100 font-sans text-lg';
          if (block.type === 'thought') className = 'font-serif italic text-zinc-400 text-[1.1em] tracking-wide';
          else if (block.type === 'action') className = 'font-bold text-zinc-300';
          
          return (
            <span key={i} className={className}>
              {block.content}
              {" "}
            </span>
          );
        })}
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
      <div className="spatial-field p-8 rounded-3xl text-zinc-100 transition-all duration-500 hover:scale-[1.01]">
        {fallback?.thought && (
          <div className="font-serif italic text-zinc-400 text-lg mb-4 border-l-2 border-emerald-500/20 pl-4 py-1">
            {fallback.thought}
          </div>
        )}
        <p className="whitespace-pre-wrap leading-relaxed font-sans text-lg">
          {fallback?.content}
        </p>
      </div>
    </div>
  );
};

export default MessageRenderer;
