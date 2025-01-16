import { Button } from "@/components/ui/button";
import { Settings, User } from "lucide-react";

export function UserSettings() {
  return (
    <div className="p-4 border-t">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
            <User className="h-4 w-4" />
          </div>
          <div>
            <p className="text-sm font-medium">Usuário</p>
            <p className="text-xs text-muted-foreground">usuario@email.com</p>
          </div>
        </div>
        <Button variant="ghost" size="icon">
          <Settings className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}