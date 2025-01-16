import { PROTECTED_PATHS, isLovableGeneratedCode } from '../src/config/protected-paths';
import fs from 'fs';
import path from 'path';
import chalk from 'chalk';

function verifyFile(filePath: string): boolean {
  try {
    const content = fs.readFileSync(filePath, 'utf-8');
    if (!isLovableGeneratedCode(content)) {
      console.error(chalk.red(`❌ Arquivo não protegido: ${filePath}`));
      return false;
    }
    return true;
  } catch (error) {
    console.error(chalk.red(`❌ Erro ao verificar arquivo: ${filePath}`));
    return false;
  }
}

function verifyDirectory(dirPath: string): boolean {
  let isValid = true;
  const files = fs.readdirSync(dirPath);

  for (const file of files) {
    const fullPath = path.join(dirPath, file);
    const stat = fs.statSync(fullPath);

    if (stat.isDirectory()) {
      isValid = verifyDirectory(fullPath) && isValid;
    } else if (stat.isFile() && (file.endsWith('.tsx') || file.endsWith('.ts') || file.endsWith('.css'))) {
      isValid = verifyFile(fullPath) && isValid;
    }
  }

  return isValid;
}

function main() {
  console.log(chalk.blue('🔍 Verificando integridade do código Lovable...'));
  
  let allValid = true;
  for (const dir of Object.values(PROTECTED_PATHS) as string[]) {
    if (fs.existsSync(dir)) {
      console.log(chalk.yellow(`\nVerificando diretório: ${dir}`));
      allValid = verifyDirectory(dir) && allValid;
    }
  }

  if (allValid) {
    console.log(chalk.green('\n✅ Todos os arquivos estão corretamente protegidos!'));
    process.exit(0);
  } else {
    console.error(chalk.red('\n❌ Alguns arquivos não estão corretamente protegidos.'));
    process.exit(1);
  }
}

main(); 