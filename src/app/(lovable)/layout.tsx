/** @generated-by-lovable - DO NOT EDIT */
"use client";
import { SessionList } from '@/components/lovable/SessionList';

export default function LovableLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="grid grid-cols-[300px_1fr] h-screen">
      <aside className="border-r">
        <SessionList />
      </aside>
      <main>
        {children}
      </main>
    </div>
  );
}
/** @end-lovable */ 