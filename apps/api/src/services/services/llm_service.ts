export interface ChatMessage {
    role: 'system' | 'user' | 'assistant';
    content: string;
}

export interface LLMConfig {
    temperature?: number;
    max_tokens?: number;
    model?: string;
}

export class LLMService {
    private apiKey: string;
    private model: string;
    private apiUrl: string;

    constructor(apiKey: string, model: string = "deepseek-chat") {
        this.apiKey = apiKey;
        this.model = model;
        this.apiUrl = "https://api.deepseek.com/v1/chat/completions";
        console.debug(`🤖 LLMService initialized with model ${model}`);
    }

    async getChatCompletion(
        messages: ChatMessage[],
        config: LLMConfig = {}
    ): Promise<string> {
        try {
            const headers = {
                "Authorization": `Bearer ${this.apiKey}`,
                "Content-Type": "application/json"
            };

            const payload = {
                model: config.model || this.model,
                messages,
                temperature: config.temperature ?? 0.7,
                max_tokens: config.max_tokens ?? 1000
            };

            console.debug(`🚀 Sending request to LLM with ${messages.length} messages`);

            const response = await fetch(this.apiUrl, {
                method: 'POST',
                headers,
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`LLM API error: ${response.statusText}`);
            }

            const result = await response.json();
            const content = result.choices[0].message.content;
            console.debug("✅ Received response from LLM");

            return content;

        } catch (error) {
            console.error("❌ Error getting LLM completion:", error);
            throw error;
        }
    }

    formatChatHistory(
        messages: ChatMessage[],
        systemPrompt?: string
    ): ChatMessage[] {
        const formatted: ChatMessage[] = [];

        if (systemPrompt) {
            formatted.push({
                role: 'system',
                content: systemPrompt
            });
        }

        return [...formatted, ...messages];
    }
} 