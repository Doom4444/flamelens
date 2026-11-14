import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { PageHeader } from '../components/common/PageHeader';
import { EmptyState } from '../components/common/EmptyState';
import { Send, BookOpen } from 'lucide-react';

export const Assistant: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const queryParam = searchParams.get('query') || '';
  const [prompt, setPrompt] = useState(queryParam);

  useEffect(() => {
    if (queryParam) {
      setPrompt(queryParam);
    }
  }, [queryParam]);

  return (
    <div className="space-y-6">
      <PageHeader
        title="AI Scientific Assistant"
        subtitle="Conversational intelligence grounded in NASA microgravity combustion flight documentation."
        badge="Phase 6 RAG Engine"
      />

      <div className="p-5 rounded-lg bg-[#111E30] border border-[#243449]">
        <label
          htmlFor="prompt-input"
          className="block text-xs font-mono uppercase text-[#35C6E8] mb-2"
        >
          Ask a Scientific Query
        </label>
        <div className="flex gap-3">
          <input
            id="prompt-input"
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="e.g. Which experiments measured fuel droplet extinction in microgravity?"
            className="flex-1 px-4 py-2.5 rounded-md bg-[#0C1626] border border-[#243449] text-sm text-[#F4F7FB] placeholder-[#64748B] focus:outline-none focus:border-[#35C6E8]"
          />
          <button
            disabled
            className="px-4 py-2.5 rounded-md bg-[#35C6E8]/40 text-[#080F1C] text-sm font-semibold flex items-center gap-2 cursor-not-allowed"
            title="AI orchestration backend will be wired in Phase 6"
          >
            <span>Ask</span>
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>

      <EmptyState
        icon={BookOpen}
        title="RAG Subsystem Scheduled for Phase 6"
        description="The AI Copilot will connect to pgvector document embeddings and Gemini/Groq providers in Phase 6 to provide traceable answers with explicit citations to NASA PSI publications."
        actionText="Back to Overview"
        onAction={() => navigate('/overview')}
      />
    </div>
  );
};
