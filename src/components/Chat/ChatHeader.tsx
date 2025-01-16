import { Button } from "@/components/ui/button";
import { MoreVertical } from "lucide-react";

export function ChatHeader() {
  return (
    <div className="border-b p-4 flex items-center justify-between">
      <div>
        <h2 className="font-semibold">Chat com Assistente</h2>
        <p className="text-sm text-muted-foreground">Conectado</p>
      </div>
      <Button variant="ghost" size="icon">
        <MoreVertical className="h-4 w-4" />
      </Button>
    </div>
  );
}