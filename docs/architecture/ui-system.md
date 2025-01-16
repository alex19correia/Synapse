# Sistema de UI/UX

## Visão Geral
```python
ui_system = {
    "framework": "Next.js 14",
    "styling": "Tailwind CSS",
    "components": "Shadcn UI",
    "status": "in_progress",
    "features": [
        "Responsive Design",
        "Dark Mode",
        "Accessibility",
        "Performance"
    ]
}
```

## Componentes Principais

### 1. Layout Base
```typescript
// src/app/layout.tsx
export default function RootLayout({
  children
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt" className="h-full">
      <body className="h-full bg-background">
        <ThemeProvider>
          <ClerkProvider>
            <Header />
            <main className="min-h-screen">
              {children}
            </main>
            <Footer />
          </ClerkProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
```

### 2. Componentes UI
```typescript
// src/components/ui/button.tsx
export const Button = React.forwardRef<
  HTMLButtonElement,
  ButtonProps
>(({ className, variant, size, ...props }, ref) => {
  return (
    <button
      className={cn(
        buttonVariants({ variant, size, className })
      )}
      ref={ref}
      {...props}
    />
  );
});
Button.displayName = "Button";
```

### 3. Temas
```typescript
// src/styles/theme.ts
export const theme = {
  colors: {
    primary: {
      DEFAULT: '#2563eb',
      dark: '#1d4ed8'
    },
    background: {
      DEFAULT: '#ffffff',
      dark: '#0f172a'
    },
    text: {
      DEFAULT: '#1e293b',
      dark: '#e2e8f0'
    }
  },
  spacing: {
    xs: '0.5rem',
    sm: '1rem',
    md: '1.5rem',
    lg: '2rem',
    xl: '3rem'
  },
  breakpoints: {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px'
  }
};
```

## Páginas

### 1. Login
```typescript
// src/app/login/page.tsx
export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <Card className="w-full max-w-md p-6">
        <CardHeader>
          <CardTitle>Login</CardTitle>
          <CardDescription>
            Entre com sua conta para continuar
          </CardDescription>
        </CardHeader>
        <CardContent>
          <SignIn />
        </CardContent>
      </Card>
    </div>
  );
}
```

### 2. Dashboard
```typescript
// src/app/dashboard/page.tsx
export default function DashboardPage() {
  return (
    <div className="container mx-auto py-6">
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <StatsCard
          title="Usuários"
          value="1,234"
          icon={<UsersIcon />}
        />
        <StatsCard
          title="Requisições"
          value="45.6k"
          icon={<ActivityIcon />}
        />
        <StatsCard
          title="Taxa de Erro"
          value="0.1%"
          icon={<AlertCircleIcon />}
        />
      </div>
    </div>
  );
}
```

## Hooks

### 1. Tema
```typescript
// src/hooks/useTheme.ts
export function useTheme() {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  
  useEffect(() => {
    const stored = localStorage.getItem('theme');
    if (stored) {
      setTheme(stored as 'light' | 'dark');
    } else {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      setTheme(prefersDark ? 'dark' : 'light');
    }
  }, []);
  
  const toggleTheme = useCallback(() => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    document.documentElement.classList.toggle('dark');
  }, [theme]);
  
  return { theme, toggleTheme };
}
```

### 2. Responsividade
```typescript
// src/hooks/useBreakpoint.ts
export function useBreakpoint() {
  const [breakpoint, setBreakpoint] = useState<'sm' | 'md' | 'lg' | 'xl'>('sm');
  
  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth;
      if (width >= 1280) setBreakpoint('xl');
      else if (width >= 1024) setBreakpoint('lg');
      else if (width >= 768) setBreakpoint('md');
      else setBreakpoint('sm');
    };
    
    window.addEventListener('resize', handleResize);
    handleResize();
    
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  
  return breakpoint;
}
```

## Estilos

### 1. Tailwind Config
```typescript
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#2563eb',
          dark: '#1d4ed8'
        }
      },
      fontFamily: {
        sans: ['var(--font-inter)']
      }
    }
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography')
  ]
};
```

### 2. Globais
```css
/* src/styles/globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 47.4% 11.2%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
  }
  
  .dark {
    --background: 224 71% 4%;
    --foreground: 213 31% 91%;
    --muted: 223 47% 11%;
    --muted-foreground: 215.4 16.3% 56.9%;
  }
}
```

## Acessibilidade

### 1. Componentes
```typescript
// src/components/ui/visually-hidden.tsx
export const VisuallyHidden = styled('span', {
  border: 0,
  clip: 'rect(0 0 0 0)',
  height: '1px',
  margin: '-1px',
  overflow: 'hidden',
  padding: 0,
  position: 'absolute',
  width: '1px',
  whiteSpace: 'nowrap'
});
```

### 2. Hooks
```typescript
// src/hooks/useA11y.ts
export function useA11y() {
  const [announcements, setAnnouncements] = useState<string[]>([]);
  
  const announce = useCallback((message: string) => {
    setAnnouncements(prev => [...prev, message]);
  }, []);
  
  return {
    announcements,
    announce,
    AriaLive: () => (
      <div
        role="status"
        aria-live="polite"
        className="sr-only"
      >
        {announcements.join(' ')}
      </div>
    )
  };
}
```

## Performance

### 1. Imagens
```typescript
// src/components/ui/image.tsx
export function OptimizedImage({
  src,
  alt,
  ...props
}: ImageProps) {
  return (
    <div className="relative">
      <Image
        src={src}
        alt={alt}
        loading="lazy"
        placeholder="blur"
        {...props}
      />
    </div>
  );
}
```

### 2. Loading
```typescript
// src/components/ui/loading.tsx
export function LoadingSpinner({
  size = 'md'
}: {
  size?: 'sm' | 'md' | 'lg'
}) {
  return (
    <div
      className={cn(
        'animate-spin rounded-full border-t-2 border-primary',
        {
          'h-4 w-4': size === 'sm',
          'h-6 w-6': size === 'md',
          'h-8 w-8': size === 'lg'
        }
      )}
    />
  );
}
```

## Próximos Passos

### Fase 1: Setup Base
1. ✅ Configuração Tailwind
2. ✅ Componentes base
3. ⏳ Sistema de temas

### Fase 2: Componentes
1. ⏳ Biblioteca de UI
2. ❌ Documentação
3. ❌ Storybook

### Fase 3: Otimização
1. ❌ Performance
2. ❌ Acessibilidade
3. ❌ SEO

## Notas Técnicas
1. Manter consistência visual
2. Priorizar acessibilidade
3. Otimizar performance
4. Documentar componentes 