'use client';

interface CodeEditorProps {
  initialCode: string;
  onChange: (code: string) => void;
}

export function CodeEditor({ initialCode, onChange }: CodeEditorProps) {
  return (
    <textarea
      defaultValue={initialCode}
      onChange={(e) => onChange(e.target.value)}
      className="w-full h-64 bg-gray-800 text-gray-100 p-4 font-mono rounded-md"
    />
  );
} 