export * from './workflow';

export interface Suggestion {
  id: string;
  title: string;
  description: string;
  impact: 'low' | 'medium' | 'high';
}

export interface ProgressProps {
  value: number;
  total: number;
  label?: string;
}

export interface StepProps {
  title: string;
  description: string;
  onComplete: (data: any) => Promise<void>;
} 