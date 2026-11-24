import React, { useState, useRef, useEffect } from 'react';
import { Place, ChatMessage } from '../types';
import { apiUrl } from '../config';
import { PlaceCard } from './PlaceCard';
import { Send, Sparkles, Loader2 } from 'lucide-react';

interface HanaChatSidebarProps {
  sessionId: string;
  activeModel?: string;
  externalPrompt?: string;
  onClearExternalPrompt?: () => void;
  groundedPlacesCount?: number;
}

export const HanaChatSidebar: React.FC<HanaChatSidebarProps> = ({
  sessionId,
  externalPrompt,
  onClearExternalPrompt,
  groundedPlacesCount = 35,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      sender: 'hana',
      text: "Konnichiwa! I'm Hana, your AI travel companion for Mount Fuji and the Fuji Five Lakes. Tell me a bit about your trip: who are you traveling with, and do you have any mobility or walking requirements?",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);

  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const lastExternalPromptRef = useRef<string | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isStreaming]);

  // Handle external prompts (e.g. from "Ask Hana to Compare" button)
  useEffect(() => {
    if (externalPrompt && externalPrompt !== lastExternalPromptRef.current && !isStreaming) {
      lastExternalPromptRef.current = externalPrompt;
      sendMessage(externalPrompt);
      if (onClearExternalPrompt) onClearExternalPrompt();
    }
  }, [externalPrompt]);

  const sendMessage = async (textToSendOverride?: string) => {
    const textToSend = (textToSendOverride || input).trim();
    if (!textToSend || isStreaming) return;

    const userMsgId = `user_${Date.now()}`;
    const newMessages: ChatMessage[] = [
      ...messages,
      {
        id: userMsgId,
        sender: 'user',
        text: textToSend,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      },
    ];

    setMessages(newMessages);
    setInput('');
    setIsStreaming(true);

    const hanaMsgId = `hana_${Date.now()}`;
    setMessages((prev) => [
      ...prev,
      {
        id: hanaMsgId,
        sender: 'hana',
        text: '',
        places: [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      },
    ]);

    try {
      let response = await fetch(apiUrl('/api/v1/chat/stream'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          message: textToSend,
        }),
      });

      if (!response.ok || !response.body) {
        response = await fetch(apiUrl('/api/ai/chat'), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_id: sessionId,
            message: textToSend,
          }),
        });
      }

      if (!response.ok || !response.body) {
        throw new Error(`HTTP error ${response.status}`);
      }

      const contentType = response.headers?.get('content-type') || '';
      if (contentType.includes('application/json')) {
        const json = await response.json();
        const replyText = json.reply || json.text || json.message || '';
        const places = json.places || json.identified_places || [];
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === hanaMsgId
              ? { ...msg, text: replyText, places: places }
              : msg
          )
        );
      } else {
        // SSE text/event-stream
        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let accumulatedText = '';
        let placesList: Place[] = [];

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const dataStr = line.substring(6).trim();
              if (dataStr === '[DONE]') continue;

              try {
                const parsed = JSON.parse(dataStr);
                if (parsed.token) {
                  accumulatedText += parsed.token;
                  setMessages((prev) =>
                    prev.map((msg) =>
                      msg.id === hanaMsgId ? { ...msg, text: accumulatedText } : msg
                    )
                  );
                }
                if (parsed.places && Array.isArray(parsed.places)) {
                  placesList = parsed.places;
                  setMessages((prev) =>
                    prev.map((msg) =>
                      msg.id === hanaMsgId ? { ...msg, places: placesList } : msg
                    )
                  );
                }
              } catch (_) {
                // Raw text token chunk fallback
                accumulatedText += dataStr;
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === hanaMsgId ? { ...msg, text: accumulatedText } : msg
                  )
                );
              }
            }
          }
        }
      }
    } catch (err) {
      console.error('Hana chat stream error:', err);
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === hanaMsgId
            ? {
                ...msg,
                text:
                  "I apologize, but I encountered a network issue communicating with the AI backend. Please verify that the FastAPI backend is running on http://127.0.0.1:8000.",
              }
            : msg
        )
      );
    } finally {
      setIsStreaming(false);
    }
  };

  const quickPrompts = [
    'Is Oishi Park crowded? Suggest quieter alternatives.',
    'Bus from Kawaguchiko Station to Chureito Pagoda',
    'Best scenic Fuji viewpoint for elderly travelers',
  ];

  return (
    <div className="h-full flex flex-col bg-white border-l border-[#E1EAF1] select-text">
      {/* 1. Header (Matches Image 1) */}
      <div className="p-4 border-b border-[#E1EAF1] flex items-center justify-between bg-white shrink-0">
        <div className="flex items-center gap-3">
          {/* Avatar with Japanese character 八 / 伴 */}
          <div className="w-10 h-10 rounded-full bg-[#078ACB] text-white flex items-center justify-center font-bold text-sm shadow-xs">
            八
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold text-[#14283F]">Hana (ハナ)</h2>
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
            </div>
            <p className="text-[11px] text-[#718198]">Mount Fuji AI Tourism Companion</p>
          </div>
        </div>

        {/* Grounded Places Count */}
        <div className="text-[11px] font-semibold text-[#078ACB]">
          {groundedPlacesCount} Places Grounded
        </div>
      </div>

      {/* 2. Messages Scroll Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-white">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex items-start gap-2.5 ${
              msg.sender === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            {/* Hana Bot Avatar */}
            {msg.sender === 'hana' && (
              <div className="w-7 h-7 rounded-full bg-[#078ACB] text-white flex items-center justify-center text-xs shrink-0 mt-0.5 shadow-2xs">
                八
              </div>
            )}

            <div
              className={`max-w-[85%] rounded-2xl px-4 py-3 text-xs leading-relaxed shadow-2xs ${
                msg.sender === 'user'
                  ? 'bg-[#078ACB] text-white rounded-tr-xs'
                  : 'bg-[#F5F8FB] text-[#14283F] border border-[#E1EAF1] rounded-tl-xs'
              }`}
            >
              <div className="whitespace-pre-wrap">{msg.text}</div>

              {/* Recommended places cards inside chat */}
              {msg.places && msg.places.length > 0 && (
                <div className="mt-3 space-y-2 pt-2 border-t border-[#E1EAF1]">
                  <div className="text-[10px] font-bold text-[#718198] flex items-center gap-1 uppercase tracking-wider">
                    <Sparkles className="w-3 h-3 text-[#078ACB]" />
                    <span>Grounded Places ({msg.places.length})</span>
                  </div>
                  <div className="grid grid-cols-1 gap-1.5">
                    {msg.places.map((place) => (
                      <PlaceCard key={place.place_id} place={place} />
                    ))}
                  </div>
                </div>
              )}

              <span
                className={`block text-[9px] mt-1.5 ${
                  msg.sender === 'user' ? 'text-sky-100 text-right' : 'text-[#718198]'
                }`}
              >
                {msg.timestamp}
              </span>
            </div>
          </div>
        ))}

        {isStreaming && (
          <div className="flex items-center gap-2 text-xs text-[#718198] italic pl-9">
            <Loader2 className="w-3.5 h-3.5 animate-spin text-[#078ACB]" />
            <span>Hana is thinking and consulting verified knowledge...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* 3. Suggested Question Chips (Matches Image 1 bottom carousel) */}
      <div className="px-4 py-2 border-t border-[#E1EAF1] flex items-center gap-2 overflow-x-auto text-[11px] bg-[#F5F8FB]/80 no-scrollbar">
        <span className="text-[11px] font-semibold text-[#718198] shrink-0">Try:</span>
        {quickPrompts.map((prompt, i) => (
          <button
            key={i}
            onClick={() => sendMessage(prompt)}
            disabled={isStreaming}
            className="shrink-0 px-3 py-1 rounded-full bg-white border border-[#E1EAF1] text-[#425466] hover:border-[#078ACB] hover:text-[#078ACB] hover:bg-[#EBF5FB] transition-colors disabled:opacity-50 text-[11px]"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* 4. Chat Input Bar */}
      <div className="p-3 border-t border-[#E1EAF1] bg-white">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            sendMessage();
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask Hana (e.g. 'Traveling with grandmother in wheelchair')"
            disabled={isStreaming}
            className="flex-1 px-4 py-2.5 text-xs rounded-xl border border-[#E1EAF1] bg-white text-[#14283F] placeholder-[#718198] focus:outline-none focus:border-[#078ACB] focus:ring-1 focus:ring-[#078ACB] disabled:bg-slate-50 transition-all"
          />
          <button
            type="submit"
            disabled={!input.trim() || isStreaming}
            className="p-2.5 rounded-xl bg-[#078ACB] text-white hover:bg-[#0672A7] disabled:opacity-40 transition-colors shrink-0 shadow-2xs"
            aria-label="Send message"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};
