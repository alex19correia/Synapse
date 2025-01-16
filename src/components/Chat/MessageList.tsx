import { ScrollArea } from "@/components/ui/scroll-area";
import { Card } from "@/components/ui/card";

export function MessageList() {
  return (
    <ScrollArea className="flex-1 p-4">
      <div className="space-y-4">
        <Card className="p-4">
          <div className="flex items-start gap-4">
            <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
              U
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium mb-1">Usuário</p>
              <p className="text-sm text-muted-foreground">
                Como posso ajudar você hoje?
              </p>
            </div>
          </div>
        </Card>
        <Card className="p-4 bg-primary/5">
          <div className="flex items-start gap-4">
            <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground">
              A
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium mb-1">Assistente</p>
              <p className="text-sm">
                Olá! Estou aqui para ajudar. Como posso ser útil?
              </p>
            </div>
          </div>
        </Card>
      </div>
    </ScrollArea>
  );
}