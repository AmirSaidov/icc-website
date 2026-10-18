'use client';

import {useEffect, useId, useRef, useState, type KeyboardEvent} from 'react';
import {Check, ChevronDown} from 'lucide-react';
import {cn} from '@/lib/cn';

export type SelectOption = {value: string; label: string};

/**
 * Выпадающий список вместо системного <select> (паттерн ARIA listbox):
 * стрелки / Home / End — выбор пункта, Enter и пробел — подтвердить, Esc — закрыть.
 */
export function Select({
  label,
  value,
  options,
  onChange,
  className
}: {
  label: string;
  value: string;
  options: SelectOption[];
  onChange: (value: string) => void;
  className?: string;
}) {
  const id = useId();
  const rootRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const listRef = useRef<HTMLUListElement>(null);
  const [open, setOpen] = useState(false);
  const selectedIndex = Math.max(0, options.findIndex((o) => o.value === value));
  const [active, setActive] = useState(selectedIndex);

  useEffect(() => {
    if (!open) return;
    const onPointer = (event: PointerEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) setOpen(false);
    };
    document.addEventListener('pointerdown', onPointer);
    return () => document.removeEventListener('pointerdown', onPointer);
  }, [open]);

  useEffect(() => {
    if (open) listRef.current?.focus();
  }, [open]);

  useEffect(() => {
    if (open) listRef.current?.querySelector(`[data-index="${active}"]`)?.scrollIntoView({block: 'nearest'});
  }, [open, active]);

  const show = () => {
    setActive(selectedIndex);
    setOpen(true);
  };
  const close = () => {
    setOpen(false);
    buttonRef.current?.focus();
  };
  const choose = (index: number) => {
    close();
    if (options[index].value !== value) onChange(options[index].value);
  };

  const onButtonKey = (event: KeyboardEvent) => {
    if (['ArrowDown', 'ArrowUp', 'Enter', ' '].includes(event.key)) {
      event.preventDefault();
      show();
    }
  };
  const onListKey = (event: KeyboardEvent) => {
    const last = options.length - 1;
    const moves: Record<string, () => void> = {
      ArrowDown: () => setActive((i) => Math.min(last, i + 1)),
      ArrowUp: () => setActive((i) => Math.max(0, i - 1)),
      Home: () => setActive(0),
      End: () => setActive(last),
      Enter: () => choose(active),
      ' ': () => choose(active),
      Escape: close,
      Tab: () => setOpen(false)
    };
    const move = moves[event.key];
    if (!move) return;
    if (event.key !== 'Tab') event.preventDefault();
    move();
  };

  return (
    <div ref={rootRef} className={cn('relative inline-flex min-w-0 flex-col gap-1.5', className)}>
      <span id={`${id}-label`} className="text-sm font-medium text-muted">
        {label}
      </span>
      <button
        ref={buttonRef}
        type="button"
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-labelledby={`${id}-label ${id}-value`}
        onClick={() => (open ? close() : show())}
        onKeyDown={onButtonKey}
        className={cn(
          'flex min-h-11 w-full min-w-56 items-center justify-between gap-3 rounded-lg border bg-surface px-4 text-left transition-[border-color,box-shadow] duration-200',
          open
            ? 'border-primary shadow-[0_0_0_3px_var(--color-primary-light)]'
            : 'border-border hover:border-primary/50'
        )}
      >
        <span id={`${id}-value`} className="truncate">
          {options[selectedIndex]?.label}
        </span>
        <ChevronDown
          aria-hidden
          className={cn('size-4 shrink-0 text-muted transition-transform duration-200', open && 'rotate-180 text-primary')}
        />
      </button>
      <ul
        ref={listRef}
        role="listbox"
        tabIndex={-1}
        aria-labelledby={`${id}-label`}
        aria-activedescendant={open ? `${id}-option-${active}` : undefined}
        onKeyDown={onListKey}
        className={cn(
          'absolute left-0 right-0 top-full z-30 mt-2 max-h-72 origin-top overflow-y-auto rounded-lg border border-border bg-surface p-1.5 shadow-lg outline-none transition duration-150 ease-out',
          open ? 'visible translate-y-0 scale-100 opacity-100' : 'invisible -translate-y-1 scale-95 opacity-0'
        )}
      >
        {options.map((option, index) => {
          const selected = index === selectedIndex;
          return (
            <li
              key={option.value}
              id={`${id}-option-${index}`}
              data-index={index}
              role="option"
              aria-selected={selected}
              onPointerEnter={() => setActive(index)}
              onClick={() => choose(index)}
              className={cn(
                'flex cursor-pointer items-center justify-between gap-3 rounded-md px-3 py-2.5 transition-colors',
                index === active && 'bg-primary-light',
                selected ? 'font-medium text-primary' : 'text-text'
              )}
            >
              <span className="truncate">{option.label}</span>
              {selected && <Check aria-hidden className="size-4 shrink-0" />}
            </li>
          );
        })}
      </ul>
    </div>
  );
}
