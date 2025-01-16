import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { MessageSquarePlus } from "lucide-react";

export function ConversationList() {
  return (
    <div className="flex-1 flex flex-col">
      <div className="p-4 border-b">
        <Button className="w-full justify-start" variant="secondary">
          <MessageSquarePlus className="mr-2 h-4 w-4" />
          Nova Conversa
        </Button>
      </div>
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-2">
          {/* Placeholder para lista de conversas */}
          <Button variant="ghost" className="w-full justify-start">
            Conversa 1
          </Button>
          <Button variant="ghost" className="w-full justify-start">
            Conversa 2
          </Button>
        </div>
      </ScrollArea>
    </div>
  );
}