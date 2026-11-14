import React, { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  AlertTriangle,
  Bot,
  ExternalLink,
  Loader2,
  Send,
  ShieldCheck,
  Sparkles,
  User,
} from 'lucide-react';
import { PageHeader } from '../components/common/PageHeader';
import { Badge } from '../components/common/Badge';
import { askAssistant } from '../services/api';
import { AssistantResponse } from '../types';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  response?: AssistantResponse;
  isError?: boolean;
}

const SUGGESTIONS = [
  'Which investigations study flame spread over solid fuels?',
  'What does PSI-25 BASS-II investigate?',
  'Which experiments use the Combustion Integrated Rack?',
  'What file formats are inventoried for PSI-25?',
];

const initialMessage: ChatMessage = {
  id: 'intro',
  role: 'assistant',
  content:
    'I search the available NASA PSI investigation metadata and return the evidence I find. Ask about objectives, approach, platforms, hardware, keywords, or audited file inventories. I will say when the metadata does not contain an answer, and I never invent measurements.',
};

function renderInline(text: string): React.ReactNode[] {
  return text
    .split(/(\*\*[^*]+\*\*)/g)
    .filter(Boolean)
    .map((part, index) =>
      part.startsWith('**') && part.endsWith('**') ? (
        <strong key={index} className="font-semibold text-[#F4F7FB]">
          {part.slice(2, -2)}
        </strong>
      ) : (
        <React.Fragment key={index}>{part}</React.Fragment>
      )
    );
}

const AnswerText: React.FC<{ text: string }> = ({ text }) => (
  <div className="space-y-1.5">
    {text
      .split('\n')
      .filter((line) => line.trim().length > 0)
      .map((line, index) =>
        line.trim().startsWith('- ') ? (
          <div key={index} className="flex gap-2">
            <span className="mt-2 h-1 w-1 flex-shrink-0 rounded-full bg-[#35C6E8]" />
            <p className="text-sm leading-relaxed text-[#D5DEEA]">
              {renderInline(line.trim().slice(2))}
            </p>
          </div>
        ) : (
          <p key={index} className="text-sm leading-relaxed text-[#D5DEEA]">
            {renderInline(line)}
          </p>
        )
      )}
  </div>
);

export const Assistant: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([initialMessage]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [messages, loading]);

  const submit = async (question: string) => {
    const trimmed = question.trim();
    if (!trimmed || loading) return;

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: trimmed,
    };
    setMessages((current) => [...current, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await askAssistant(trimmed, 4);
      setMessages((current) => [
        ...current,
        {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: response.answer,
          response,
        },
      ]);
    } catch (err) {
      setMessages((current) => [
        ...current,
        {
          id: `error-${Date.now()}`,
          role: 'assistant',
          content:
            err instanceof Error
              ? `The assistant request failed: ${err.message}. No answer was fabricated.`
              : 'The assistant request failed. No answer was fabricated.',
          isError: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto flex max-w-4xl flex-col space-y-5">
      <PageHeader
        title="Metadata Assistant"
        subtitle="Retrieval over the audited NASA PSI investigation metadata. Evidence is cited by investigation ID and title; absent evidence is stated explicitly."
        badge="Grounded retrieval"
      />

      <div className="flex items-start gap-2.5 rounded-lg border border-[#243449] bg-[#0C1626]/60 p-3.5">
        <ShieldCheck className="mt-0.5 h-4 w-4 flex-shrink-0 text-[#35C6E8]" />
        <p className="text-[11px] leading-relaxed text-[#94A3B8]">
          This assistant answers only from inventory metadata and file records already held
          by FlameLens. It never reports experimental measurements, never claims a file is
          downloaded, and never asserts scientific comparability. If the backend has a
          configured LLM key, the same retrieved evidence is passed to it with a grounding
          prompt; otherwise deterministic retrieval composes the answer.
        </p>
      </div>

      <div className="space-y-4">
        {messages.map((message) => (
          <div key={message.id} className="flex gap-3">
            <div
              className={`mt-0.5 flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-md border ${
                message.role === 'user'
                  ? 'border-[#FF914D]/30 bg-[#FF914D]/10 text-[#FF914D]'
                  : 'border-[#35C6E8]/30 bg-[#35C6E8]/10 text-[#35C6E8]'
              }`}
            >
              {message.role === 'user' ? (
                <User className="h-4 w-4" />
              ) : (
                <Bot className="h-4 w-4" />
              )}
            </div>

            <div className="min-w-0 flex-1">
              <div
                className={`rounded-lg border p-4 ${
                  message.isError
                    ? 'border-rose-400/30 bg-rose-400/5'
                    : 'border-[#243449] bg-[#111E30]'
                }`}
              >
                {message.response && (
                  <div className="mb-2 flex flex-wrap items-center gap-2">
                    <Badge tone={message.response.answer_type === 'llm_grounded' ? 'purple' : 'cyan'}>
                      {message.response.answer_type === 'llm_grounded'
                        ? `LLM grounded · ${message.response.provider}`
                        : 'Deterministic metadata retrieval'}
                    </Badge>
                    <Badge tone="slate">
                      {message.response.citations.length} cited record
                      {message.response.citations.length === 1 ? '' : 's'}
                    </Badge>
                  </div>
                )}
                <AnswerText text={message.content} />

                {message.response && message.response.citations.length > 0 && (
                  <div className="mt-4 space-y-2 border-t border-[#243449]/60 pt-3">
                    <p className="font-mono text-[10px] uppercase tracking-wider text-[#64748B]">
                      Evidence
                    </p>
                    {message.response.citations.map((citation) => (
                      <div
                        key={`${citation.investigation_id}-${citation.field}`}
                        className="rounded-md border border-[#243449]/70 bg-[#0C1626]/50 p-3"
                      >
                        <div className="mb-1 flex flex-wrap items-center justify-between gap-2">
                          <Link
                            to={`/investigations/${citation.investigation_id}`}
                            className="inline-flex items-center gap-1.5 font-mono text-xs text-[#35C6E8] hover:text-[#F4F7FB]"
                          >
                            {citation.investigation_id} · {citation.title}
                            <ExternalLink className="h-3 w-3" />
                          </Link>
                          <span className="font-mono text-[10px] text-[#64748B]">
                            {citation.field} · score {citation.score.toFixed(2)}
                          </span>
                        </div>
                        <p className="text-[11px] leading-relaxed text-[#94A3B8]">
                          {citation.snippet}
                        </p>
                        {citation.matched_terms.length > 0 && (
                          <div className="mt-1.5 flex flex-wrap gap-1">
                            {citation.matched_terms.map((term) => (
                              <Badge key={term} tone="slate">
                                {term}
                              </Badge>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {message.response && message.response.disclaimers.length > 0 && (
                  <div className="mt-3 border-t border-[#243449]/60 pt-2.5">
                    {message.response.disclaimers.map((disclaimer) => (
                      <p
                        key={disclaimer}
                        className="flex gap-1.5 text-[10px] leading-relaxed text-[#64748B]"
                      >
                        <AlertTriangle className="mt-0.5 h-3 w-3 flex-shrink-0 text-[#FF914D]" />
                        {disclaimer}
                      </p>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex gap-3">
            <div className="mt-0.5 flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-md border border-[#35C6E8]/30 bg-[#35C6E8]/10 text-[#35C6E8]">
              <Bot className="h-4 w-4" />
            </div>
            <div className="flex items-center gap-2 rounded-lg border border-[#243449] bg-[#111E30] px-4 py-3 text-xs text-[#94A3B8]">
              <Loader2 className="h-3.5 w-3.5 animate-spin text-[#35C6E8]" />
              Retrieving evidence from investigation metadata...
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {messages.length <= 1 && (
        <div className="space-y-2">
          <p className="font-mono text-[10px] uppercase tracking-wider text-[#64748B]">
            Suggested questions
          </p>
          <div className="flex flex-wrap gap-2">
            {SUGGESTIONS.map((suggestion) => (
              <button
                key={suggestion}
                onClick={() => submit(suggestion)}
                disabled={loading}
                className="rounded-full border border-[#243449] bg-[#111E30] px-3 py-1.5 text-left text-[11px] text-[#94A3B8] transition-colors hover:border-[#35C6E8] hover:text-[#35C6E8] disabled:opacity-50"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}

      <form
        onSubmit={(event) => {
          event.preventDefault();
          submit(input);
        }}
        className="sticky bottom-4 rounded-lg border border-[#243449] bg-[#111E30] p-3 shadow-lg"
      >
        <div className="flex items-end gap-2">
          <textarea
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                submit(input);
              }
            }}
            rows={2}
            maxLength={500}
            placeholder="Ask about objectives, approach, platforms, hardware, or file inventories..."
            className="min-h-[2.75rem] flex-1 resize-none rounded-md border border-[#243449] bg-[#0C1626] px-3 py-2 text-sm text-[#F4F7FB] outline-none transition-colors placeholder:text-[#64748B] focus:border-[#35C6E8]"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="inline-flex h-11 items-center gap-2 rounded-md border border-[#35C6E8]/40 bg-[#35C6E8]/10 px-4 text-sm font-medium text-[#35C6E8] transition-colors hover:bg-[#35C6E8]/20 disabled:cursor-not-allowed disabled:opacity-40"
          >
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
            Ask
          </button>
        </div>
        <p className="mt-2 flex items-center gap-1.5 font-mono text-[10px] text-[#64748B]">
          <Sparkles className="h-3 w-3 text-[#35C6E8]" />
          Enter to send · Shift+Enter for a new line · answers are bounded to retrieved
          metadata
        </p>
      </form>
    </div>
  );
};
