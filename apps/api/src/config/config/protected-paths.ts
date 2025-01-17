export const PROTECTED_PATHS = {
  components: 'src/components/lovable',
  pages: 'src/app/(lovable)',
  styles: 'src/styles/lovable',
} as const;

export const LOVABLE_COMMENT_MARKERS = {
  start: '/** @generated-by-lovable - DO NOT EDIT */',
  end: '/** @end-lovable */',
} as const;

export function isProtectedPath(path: string): boolean {
  return Object.values(PROTECTED_PATHS).some(
    protectedPath => path.startsWith(protectedPath)
  );
}

export function isLovableGeneratedCode(content: string): boolean {
  return (
    content.includes(LOVABLE_COMMENT_MARKERS.start) &&
    content.includes(LOVABLE_COMMENT_MARKERS.end)
  );
} 