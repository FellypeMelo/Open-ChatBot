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
  isLatest?: boolean;
}

const RevealingText: React.FC<{ text: string; isLatest: boolean }> = ({ text, isLatest }) => {
  if (!isLatest) return <>{text}</>;

  // Split text into words, then group into clusters of 3-5
  const words = text.split(/(\s+)/); // Preserve whitespace
  const clusters: string[] = [];
  let currentCluster: string[] = [];
  let wordCount = 0;
  const targetWordsPerCluster = 4;

  for (let i = 0; i < words.length; i++) {
    const part = words[i];
    currentCluster.push(part);
    if (part.trim().length > 0) {
      wordCount++;
    }

    if (wordCount >= targetWordsPerCluster || i === words.length - 1) {
      clusters.push(currentCluster.join(''));
      currentCluster = [];
      wordCount = 0;
    }
  }

  return (
    <>
      {clusters.map((cluster, i) => (
        <span
          key={i}
          className="inline-block opacity-0 animate-word-reveal"
          style={{ animationDelay: `${i * 0.8}s` }}
        >
          {cluster}
        </span>
      ))}
    </>
  );
};

const MessageRenderer: React.FC<MessageRendererProps> = ({ sequence, fallback, isLatest = false }) => {
  if (sequence && sequence.length > 0) {
    return (
      <div className="message-container leading-relaxed spatial-field p-8 rounded-3xl transition-all duration-500 hover:scale-[1.01]">
        {sequence.map((block, i) => {
          let className = 'text-zinc-100 font-sans text-lg';
          if (block.type === 'thought') className = 'font-serif italic text-zinc-400 text-[1.1em] tracking-wide';
          else if (block.type === 'action') className = 'font-bold text-zinc-300';
          
          return (
            <span key={i} className={className}>
              <RevealingText text={block.content} isLatest={isLatest} />
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
            <RevealingText text={fallback.thought} isLatest={isLatest} />
          </div>
        )}
        <div className="whitespace-pre-wrap leading-relaxed font-sans text-lg">
          <RevealingText text={fallback?.content || ''} isLatest={isLatest} />
        </div>
      </div>
    </div>
  );
};

export default MessageRenderer;
