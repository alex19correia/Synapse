'use client';

import React from 'react';
import { useTutorial } from '@/app/hooks/useTutorial';
import { CodeEditor } from '@/app/components/Tutorial/CodeEditor';
import { TutorialStep } from '@/app/components/Tutorial/TutorialStep';

export const InteractiveTutorial: React.FC<{
    tutorialId: string;
}> = ({ tutorialId }) => {
    const {
        currentStep,
        tutorial,
        checkSolution,
        progress,
        loading
    } = useTutorial(tutorialId);

    if (loading) return <div>Loading tutorial...</div>;
    if (!tutorial) return <div>Tutorial not found</div>;

    return (
        <div className="grid grid-cols-2 gap-6">
            <div className="tutorial-content">
                <TutorialStep
                    step={tutorial.steps[currentStep]}
                    progress={progress}
                />
            </div>
            
            <div className="code-playground">
                <CodeEditor
                    initialCode={tutorial.steps[currentStep].startingCode}
                    onChange={async (code) => {
                        const isCorrect = await checkSolution(code);
                        if (isCorrect) {
                            // Avança para próximo passo
                        }
                    }}
                />
            </div>
        </div>
    );
}; 