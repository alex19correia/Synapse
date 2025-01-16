import { ReactNode } from "react";

interface ChatLayoutProps {
  children: ReactNode;
}

export function ChatLayout({ children }: ChatLayoutProps) {
  return (
    <div className="h-screen flex flex-col bg-background">
      <div className="flex-1 overflow-hidden">{children}</div>
    </div>
  );
}