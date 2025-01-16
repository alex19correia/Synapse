import { LOVABLE_COMMENT_MARKERS, PROTECTED_PATHS } from '../src/config/protected-paths';
import fs from 'fs';
import path from 'path';

function wrapWithProtection(code: string): string {
  return `${LOVABLE_COMMENT_MARKERS.start}
${code}
${LOVABLE_COMMENT_MARKERS.end}`;
}

function createProtectedDirectories(): void {
  Object.values(PROTECTED_PATHS).forEach(dir => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  });
}

function protectLovableCode(sourcePath: string, destinationPath: string): void {
  const content = fs.readFileSync(sourcePath, 'utf-8');
  const protectedContent = wrapWithProtection(content);
  
  const destDir = path.dirname(destinationPath);
  if (!fs.existsSync(destDir)) {
    fs.mkdirSync(destDir, { recursive: true });
  }
  
  fs.writeFileSync(destinationPath, protectedContent);
}

// Exemplo de uso:
// protectLovableCode('lovable-export/Component.tsx', 'src/components/lovable/Component.tsx'); 