import { useState, useEffect } from 'react';

export type BlockType = 'speech' | 'thought' | 'action';

export interface Atmosphere {
  blurAmount: number;
  textOpacity: number;
  blockType: BlockType;
}

export const useAtmosphere = (text: string): Atmosphere => {
  const [atmosphere, setAtmosphere] = useState<Atmosphere>({
    blurAmount: 0,
    textOpacity: 1,
    blockType: 'speech',
  });

  useEffect(() => {
    // Detect current block type by looking at the end of the text
    let currentType: BlockType = 'speech';
    
    // Check if we are inside a thought block (*) but not action (**)
    // We look for the last occurrence of *
    const lastDoubleStar = text.lastIndexOf('**');
    const lastSingleStar = text.lastIndexOf('*');

    if (lastDoubleStar !== -1 && (lastSingleStar === -1 || lastDoubleStar > lastSingleStar - 1)) {
        // We might be in an action block
        // Check if it's closed
        const openingCount = (text.match(/\*\*/g) || []).length;
        if (openingCount % 2 !== 0) {
            currentType = 'action';
        }
    } else if (lastSingleStar !== -1) {
        // We might be in a thought block
        // Check if it's closed
        const openingCount = (text.match(/(?<!\*)\*(?!\*)/g) || []).length;
        if (openingCount % 2 !== 0) {
            currentType = 'thought';
        }
    }

    // Map block type to atmosphere values
    switch (currentType) {
      case 'thought':
        setAtmosphere({
          blurAmount: 8, // Deep blur for internal thoughts
          textOpacity: 0.7,
          blockType: 'thought',
        });
        break;
      case 'action':
        setAtmosphere({
          blurAmount: 2, // Slight focus blur for actions
          textOpacity: 1,
          blockType: 'action',
        });
        break;
      case 'speech':
      default:
        setAtmosphere({
          blurAmount: 0,
          textOpacity: 1,
          blockType: 'speech',
        });
        break;
    }
  }, [text]);

  return atmosphere;
};
