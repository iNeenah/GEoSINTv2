import React, { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import SplitType from 'split-type';

interface TextAnimatorProps {
  children: React.ReactNode;
  className?: string;
  trigger?: 'hover' | 'auto' | 'click';
  delay?: number;
  colors?: string[];
  onAnimationComplete?: () => void;
}

const lettersAndSymbols = [
  'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
  '!', '@', '#', '$', '%', '^', '&', '*', '-', '_', '+', '=', ';', ':', '<', '>', ',', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'
];

const defaultColors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe'];

export const TextAnimator: React.FC<TextAnimatorProps> = ({
  children,
  className = '',
  trigger = 'hover',
  delay = 0,
  colors = defaultColors,
  onAnimationComplete
}) => {
  const textRef = useRef<HTMLSpanElement>(null);
  const splitTextRef = useRef<SplitType | null>(null);
  const originalCharsRef = useRef<string[]>([]);
  const originalColorsRef = useRef<string[]>([]);
  const isAnimatingRef = useRef(false);

  useEffect(() => {
    if (!textRef.current) return;

    // Initialize SplitType
    splitTextRef.current = new SplitType(textRef.current, {
      types: 'words,chars'
    });

    // Store original characters and colors
    const chars = splitTextRef.current.chars || [];
    originalCharsRef.current = chars.map(char => char.innerHTML);
    originalColorsRef.current = chars.map(char => getComputedStyle(char).color);

    return () => {
      if (splitTextRef.current) {
        splitTextRef.current.revert();
      }
    };
  }, [children]);

  useEffect(() => {
    if (trigger === 'auto' && textRef.current) {
      const timer = setTimeout(() => {
        animate();
      }, delay);
      return () => clearTimeout(timer);
    }
  }, [trigger, delay]);

  const animate = () => {
    if (!splitTextRef.current || isAnimatingRef.current) return;
    
    isAnimatingRef.current = true;
    const chars = splitTextRef.current.chars || [];

    // Reset any ongoing animations
    chars.forEach((char, index) => {
      gsap.killTweensOf(char);
      char.innerHTML = originalCharsRef.current[index];
      char.style.color = originalColorsRef.current[index];
    });

    chars.forEach((char, position) => {
      const initialHTML = char.innerHTML;
      const initialColor = getComputedStyle(char).color;

      gsap
        .timeline()
        .fromTo(char, {
          opacity: 1, // Keep text visible
          transformOrigin: '50% 0%'
        }, {
          duration: 0.03,
          ease: 'none',
          onComplete: () => {
            gsap.set(char, { 
              innerHTML: initialHTML, 
              color: initialColor, 
              delay: 0.03 
            });
            if (position === chars.length - 1) {
              isAnimatingRef.current = false;
              onAnimationComplete?.();
            }
          },
          repeat: 3,
          repeatRefresh: true,
          repeatDelay: 0.1,
          delay: (position + 1) * 0.08,
          innerHTML: () => {
            const randomChar = lettersAndSymbols[Math.floor(Math.random() * lettersAndSymbols.length)];
            const randomColor = colors[Math.floor(Math.random() * colors.length)];
            gsap.set(char, { color: randomColor });
            return randomChar;
          },
          opacity: 1
        });
    });
  };

  const handleMouseEnter = () => {
    if (trigger === 'hover') {
      animate();
    }
  };

  const handleClick = () => {
    if (trigger === 'click') {
      animate();
    }
  };

  return (
    <span
      ref={textRef}
      className={`text-animator ${className}`}
      onMouseEnter={handleMouseEnter}
      onClick={handleClick}
      style={{ cursor: trigger === 'click' ? 'pointer' : 'default' }}
    >
      {children}
    </span>
  );
};

export default TextAnimator;