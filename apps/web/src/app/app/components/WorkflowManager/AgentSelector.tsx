'use client';

interface AgentSelectorProps {
  selectedAgents: string[];
  onSelect: (agents: string[]) => void;
}

const availableAgents = [
  'Web Researcher',
  'Tech Stack Expert',
  'GitHub Assistant',
  'Local AI Expert'
];

export function AgentSelector({ selectedAgents, onSelect }: AgentSelectorProps) {
  const toggleAgent = (agent: string) => {
    if (selectedAgents.includes(agent)) {
      onSelect(selectedAgents.filter(a => a !== agent));
    } else {
      onSelect([...selectedAgents, agent]);
    }
  };

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Select Agents</h3>
      <div className="grid grid-cols-2 gap-4">
        {availableAgents.map(agent => (
          <button
            key={agent}
            onClick={() => toggleAgent(agent)}
            className={`p-3 rounded-md text-left transition-colors ${
              selectedAgents.includes(agent)
                ? 'bg-blue-500 hover:bg-blue-600'
                : 'bg-gray-700 hover:bg-gray-600'
            }`}
          >
            {agent}
          </button>
        ))}
      </div>
    </div>
  );
} 