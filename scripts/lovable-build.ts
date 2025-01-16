const fs = require('fs');
const path = require('path');
const chalk = require('chalk');
const { PROTECTED_PATHS } = require('../src/config/protected-paths');

async function buildLovableComponents() {
  console.log(chalk.blue('🏗️ Iniciando build dos componentes Lovable...'));

  // Verifica se os diretórios existem
  Object.entries(PROTECTED_PATHS).forEach(([key, dir]) => {
    if (!fs.existsSync(dir)) {
      console.log(chalk.yellow(`Criando diretório ${key}: ${dir}`));
      fs.mkdirSync(dir, { recursive: true });
    }
  });

  // Aqui você pode adicionar lógica adicional de build
  // Por exemplo, compilação de TypeScript, minificação, etc.
  console.log(chalk.green('✅ Diretórios verificados e criados'));

  // Gera um arquivo de manifesto
  const manifest = {
    buildDate: new Date().toISOString(),
    directories: PROTECTED_PATHS,
    version: process.env.npm_package_version || '0.0.1'
  };

  const manifestPath = path.join(PROTECTED_PATHS.components, 'lovable.manifest.json');
  fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2));
  console.log(chalk.green('✅ Manifesto gerado'));

  console.log(chalk.blue('\n📝 Próximos passos:'));
  console.log('1. Exporte seus componentes do Lovable');
  console.log('2. Execute npm run protect-lovable');
  console.log('3. Verifique a integridade com npm run verify-lovable');
}

buildLovableComponents().catch(error => {
  console.error(chalk.red('❌ Erro durante o build:'), error);
  process.exit(1);
}); 