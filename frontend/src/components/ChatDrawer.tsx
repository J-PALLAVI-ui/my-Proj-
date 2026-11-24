import React, { useState, useRef, useEffect } from 'react';
import { Place, ChatMessage, Journey, CrowdAlternativeCard, ItineraryPlan } from '../types';
import { apiUrl } from '../config';
import { JourneyDisplay } from './JourneyDisplay';
import { PlaceCard } from './PlaceCard';
import { 
  Send, 
  Bot, 
  User, 
  Sparkles, 
  Loader2, 
  Users, 
  Copy, 
  Check, 
  RotateCcw, 
  Trash2, 
  Cpu
} from 'lucide-react';

interface ChatDrawerProps {
  sessionId: string;
  onProfileUpdated?: (profile: any) => void;
  onItineraryUpdated?: (itinerary: ItineraryPlan) => void;
  externalPrompt?: string;
  activeModel?: string;
}

export const ChatDrawer: React.FC<ChatDrawerProps> = ({ 
  sessionId, 
  onProfileUpdated, 
  onItineraryUpdated,
  externalPrompt,
  activeModel = 'gpt-4o-mini'
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      sender: 'hana',
      text: "Konnichiwa! I'm Hana (ハナ), your AI travel companion for Mount Fuji and the Fuji Five Lakes. I can answer any general questions (including culture, technology, translations, and weather) or plan personalized itineraries with verified public transport schedules. How can I assist you today?",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [lastUserPrompt, setLastUserPrompt] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const lastExternalPromptRef = useRef<string | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isStreaming]);

  useEffect(() => {
    if (externalPrompt && externalPrompt !== lastExternalPromptRef.current && !isStreaming) {
      lastExternalPromptRef.current = externalPrompt;
      sendMessage(externalPrompt);
    }
  }, [externalPrompt]);

  const handleCopyText = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleClearSession = async () => {
    try {
      await fetch(apiUrl(`/api/v1/sessions/${sessionId}`), { method: 'DELETE' });
    } catch (_) {}
    setMessages([
      {
        id: `welcome_${Date.now()}`,
        sender: 'hana',
        text: "Conversation cleared. How can I assist you with your Mount Fuji travels, culture, or general questions?",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    ]);
  };

  const handleRetry = () => {
    if (lastUserPrompt && !isStreaming) {
      sendMessage(lastUserPrompt);
    }
  };

  const sendMessage = async (messageText?: string) => {
    const textToSend = messageText || input;
    if (!textToSend.trim() || isStreaming) return;

    setLastUserPrompt(textToSend);
    const userMsgId = `user_${Date.now()}`;
    const newMessages: ChatMessage[] = [
      ...messages,
      {
        id: userMsgId,
        sender: 'user',
        text: textToSend,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    ];

    setMessages(newMessages);
    setInput('');
    setIsStreaming(true);

    const hanaMsgId = `hana_${Date.now()}`;
    // Create empty Hana message placeholder for streaming
    setMessages((prev) => [
      ...prev,
      {
        id: hanaMsgId,
        sender: 'hana',
        text: '',
        places: [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    ]);

    try {
      let response = await fetch(apiUrl('/api/v1/chat/stream'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          message: textToSend
        })
      });

      if (!response.ok || !response.body) {
        response = await fetch(apiUrl('/api/ai/chat'), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_id: sessionId,
            message: textToSend
          })
        });
      }

      if (!response.ok || !response.body) {
        throw new Error(`HTTP error ${response.status}`);
      }

      const contentType = response.headers?.get('content-type') || '';
      if (contentType.includes('application/json')) {
        const json = await response.json();
        const replyText = json.reply || json.text || json.message || '';
        const journeys = json.journeys || json.identified_journeys || [];
        const places = json.places || json.identified_places || [];
        const itinerary = json.itinerary || json.active_itinerary;
        if (itinerary && onItineraryUpdated) {
          onItineraryUpdated(itinerary);
        }
        setMessages((prev) =>
          prev.map((m) =>
            m.id === hanaMsgId
              ? {
                  ...m,
                  text: replyText || (journeys.length > 0 ? 'Here is the verified transit route for your journey:' : ''),
                  journeys: journeys.length > 0 ? journeys : m.journeys,
                  places: places.length > 0 ? places : m.places
                }
              : m
          )
        );
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const events = buffer.split('\n\n');
        buffer = events.pop() || '';

        for (const eventBlock of events) {
          if (!eventBlock.trim()) continue;
          const lines = eventBlock.split('\n');
          let eventType = 'message';
          let eventData = '';

          for (const line of lines) {
            if (line.startsWith('event: ')) {
              eventType = line.slice(7).trim();
            } else if (line.startsWith('data: ')) {
              eventData = line.slice(6);
            }
          }

          if (eventType === 'token') {
            try {
              const parsed = JSON.parse(eventData);
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === hanaMsgId ? { ...m, text: m.text + parsed.token } : m
                )
              );
            } catch (e) {
              console.error('Error parsing token event', e);
            }
          } else if (eventType === 'itinerary') {
            try {
              const itineraryData: ItineraryPlan = JSON.parse(eventData);
              if (onItineraryUpdated) {
                onItineraryUpdated(itineraryData);
              }
            } catch (e) {
              console.error('Error parsing itinerary event', e);
            }
          } else if (eventType === 'places') {
            try {
              const places: Place[] = JSON.parse(eventData);
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === hanaMsgId ? { ...m, places } : m
                )
              );
            } catch (e) {
              console.error('Error parsing places event', e);
            }
          } else if (eventType === 'transit') {
            try {
              const journeys: Journey[] = JSON.parse(eventData);
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === hanaMsgId ? { ...m, journeys } : m
                )
              );
            } catch (e) {
              console.error('Error parsing transit event', e);
            }
          } else if (eventType === 'crowd_alternatives') {
            try {
              const crowd_alternatives: CrowdAlternativeCard[] = JSON.parse(eventData);
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === hanaMsgId ? { ...m, crowd_alternatives } : m
                )
              );
            } catch (e) {
              console.error('Error parsing crowd alternatives event', e);
            }
          } else if (eventType === 'error') {
            try {
              const errData = JSON.parse(eventData);
              const errMsg = errData.error || eventData;
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === hanaMsgId
                    ? { ...m, text: m.text ? `${m.text}\n\n[Error: ${errMsg}]` : `[Error: ${errMsg}]` }
                    : m
                )
              );
            } catch {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === hanaMsgId
                    ? { ...m, text: m.text ? `${m.text}\n\n[Error: ${eventData}]` : `[Error: ${eventData}]` }
                    : m
                )
              );
            }
          } else if (eventType === 'done') {
            try {
              const doneData = JSON.parse(eventData);
              if (onProfileUpdated && doneData.profile) {
                onProfileUpdated(doneData.profile);
              }
            } catch (e) {
              console.error('Error parsing done event', e);
            }
          }
        }
      }
    } catch (err: any) {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === hanaMsgId
            ? { ...m, text: m.text + `\n\n[Communication note: ${err.message}]` }
            : m
        )
      );
    } finally {
      setIsStreaming(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const quickPrompts = [
    "What is the difference between machine learning and deep learning?",
    "Explain Japanese Omotenashi hospitality & culture",
    "Can you recommend a 1-day itinerary with best Fuji views?",
    "How do I travel from Tokyo to Mount Fuji / Kawaguchiko?",
    "What is the weather and visibility like in December?",
    "Is Oishi Park crowded? Suggest quieter alternatives."
  ];

  // Helper to render bold and lists cleanly without full heavy markdown parser
  const renderMessageContent = (content: string) => {
    return (
      <div className="whitespace-pre-wrap leading-relaxed space-y-1">
        {content.split('\n').map((line, idx) => {
          // Parse **bold** tokens
          const parts = line.split(/(\*\*.*?\*\*)/g);
          return (
            <p key={idx} className={line.startsWith('- ') || line.startsWith('* ') ? 'pl-2' : ''}>
              {parts.map((part, pIdx) => {
                if (part.startsWith('**') && part.endsWith('**')) {
                  return (
                    <strong key={pIdx} className="font-semibold">
                      {part.slice(2, -2)}
                    </strong>
                  );
                }
                return part;
              })}
            </p>
          );
        })}
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full bg-white border-r border-slate-200">
      {/* Header */}
      <div className="p-3.5 border-b border-slate-200 flex items-center justify-between bg-sky-50/50">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-full bg-sky-600 text-white flex items-center justify-center font-bold text-sm shadow-xs">
            ハ
          </div>
          <div>
            <h2 className="font-bold text-slate-900 text-xs flex items-center gap-1.5">
              Guide Hana (ハナ)
              <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block animate-pulse" title="Online" />
            </h2>
            <p className="text-[10px] text-slate-500">Conversational AI Travel Companion</p>
          </div>
        </div>

        {/* Model status & Session Reset */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 text-[10px] text-sky-800 bg-sky-100/70 border border-sky-200 px-2 py-0.5 rounded-md font-mono">
            <Cpu className="w-3 h-3 text-sky-600" />
            <span>{activeModel}</span>
          </div>
          <button
            onClick={handleClearSession}
            title="Clear Conversation"
            className="p-1 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded transition-colors"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Message Stream */}
      <div className="flex-1 overflow-y-auto p-3.5 space-y-3.5">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-2.5 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.sender === 'hana' && (
              <div className="w-6 h-6 rounded-full bg-sky-600 text-white flex items-center justify-center text-[10px] shrink-0 mt-1">
                <Bot className="w-3.5 h-3.5" />
              </div>
            )}
            <div className={`max-w-[88%] rounded-2xl px-3.5 py-2.5 text-xs relative group ${
              msg.sender === 'user'
                ? 'bg-sky-600 text-white rounded-br-xs'
                : 'bg-slate-100 text-slate-800 rounded-bl-xs'
            }`}>
              {/* Copy button on hover for assistant messages */}
              {msg.sender === 'hana' && msg.text && (
                <button
                  onClick={() => handleCopyText(msg.id, msg.text)}
                  className="absolute right-2 top-2 p-1 text-slate-400 hover:text-slate-700 rounded bg-white/70 shadow-2xs opacity-0 group-hover:opacity-100 transition-opacity"
                  title="Copy response"
                >
                  {copiedId === msg.id ? <Check className="w-3 h-3 text-emerald-600" /> : <Copy className="w-3 h-3" />}
                </button>
              )}

              {renderMessageContent(msg.text)}

              {/* Transit Connections */}
              {msg.journeys && msg.journeys.length > 0 && (
                <div className="mt-2.5">
                  <div className="text-[11px] font-semibold text-slate-600 flex items-center gap-1 mb-1">
                    <Sparkles className="w-3 h-3 text-sky-600" />
                    <span>Calculated Transit Connections ({msg.journeys.length})</span>
                  </div>
                  <JourneyDisplay journeys={msg.journeys} />
                </div>
              )}

              {/* CrowdSense Alternatives */}
              {msg.crowd_alternatives && msg.crowd_alternatives.length > 0 && (
                <div className="mt-2.5 pt-2 border-t border-slate-200/80 space-y-1.5">
                  <div className="text-[11px] font-semibold text-emerald-800 flex items-center gap-1">
                    <Users className="w-3 h-3 text-emerald-600" />
                    <span>CrowdSense Quieter Alternatives ({msg.crowd_alternatives.length})</span>
                  </div>
                  <div className="space-y-1.5">
                    {msg.crowd_alternatives.map((alt) => (
                      <div
                        key={alt.place_id}
                        className="bg-white border border-emerald-200 rounded-lg p-2 flex items-center gap-2 shadow-2xs"
                      >
                        <img
                          src={alt.image_url}
                          alt={alt.name_en}
                          className="w-10 h-10 rounded object-cover bg-slate-100 shrink-0"
                          onError={(e) => {
                            (e.currentTarget as HTMLImageElement).src =
                              'https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=400&q=80';
                          }}
                        />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between gap-1">
                            <h4 className="text-[11px] font-bold text-slate-900 truncate">{alt.name_en}</h4>
                            <span className="text-[9px] font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-1 rounded-full shrink-0">
                              -{alt.crowd_reduction_percent}%
                            </span>
                          </div>
                          <p className="text-[10px] text-slate-500 truncate">{alt.name_ja}</p>
                          <p className="text-[10px] text-slate-600 line-clamp-1">{alt.recommendation_reason}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Recommended Places */}
              {msg.places && msg.places.length > 0 && (
                <div className="mt-2.5 space-y-2 pt-2 border-t border-slate-200/80">
                  <div className="text-[11px] font-semibold text-slate-600 flex items-center gap-1">
                    <Sparkles className="w-3 h-3 text-amber-500" />
                    <span>Verified Places Grounding ({msg.places.length})</span>
                  </div>
                  <div className="grid grid-cols-1 gap-2">
                    {msg.places.map((place) => (
                      <PlaceCard key={place.place_id} place={place} />
                    ))}
                  </div>
                </div>
              )}

              <span className={`block text-[9px] mt-1 ${
                msg.sender === 'user' ? 'text-sky-200 text-right' : 'text-slate-400'
              }`}>
                {msg.timestamp}
              </span>
            </div>
            {msg.sender === 'user' && (
              <div className="w-6 h-6 rounded-full bg-slate-300 text-slate-700 flex items-center justify-center text-[10px] shrink-0 mt-1">
                <User className="w-3.5 h-3.5" />
              </div>
            )}
          </div>
        ))}

        {isStreaming && (
          <div className="flex items-center gap-2 text-xs text-slate-400 italic">
            <Loader2 className="w-3.5 h-3.5 animate-spin text-sky-600" />
            <span>Hana is thinking and consulting verified knowledge...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Prompts Carousel */}
      <div className="px-3 py-1.5 border-t border-slate-100 flex items-center gap-1.5 overflow-x-auto text-[11px] bg-slate-50/70">
        <span className="text-[10px] font-semibold text-slate-400 shrink-0">Try:</span>
        {quickPrompts.map((prompt, i) => (
          <button
            key={i}
            onClick={() => sendMessage(prompt)}
            disabled={isStreaming}
            className="shrink-0 px-2 py-0.5 rounded-full bg-white border border-slate-200 text-slate-600 hover:border-sky-300 hover:text-sky-700 hover:bg-sky-50 transition-colors disabled:opacity-50"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input Field with Multi-line Support */}
      <div className="p-2.5 border-t border-slate-200 bg-white">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            sendMessage();
          }}
          className="flex items-end gap-1.5"
        >
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask Hana anything (Shift+Enter for newline)..."
            disabled={isStreaming}
            className="flex-1 px-3 py-2 text-xs rounded-xl border border-slate-200 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500 disabled:bg-slate-50 resize-none max-h-24 leading-normal"
          />
          {lastUserPrompt && !isStreaming && (
            <button
              type="button"
              onClick={handleRetry}
              title="Retry last question"
              className="p-2 rounded-xl text-slate-400 hover:text-sky-600 hover:bg-sky-50 border border-slate-200 shrink-0 transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          )}
          <button
            type="submit"
            disabled={!input.trim() || isStreaming}
            className="p-2.5 rounded-xl bg-sky-600 text-white hover:bg-sky-700 disabled:opacity-50 transition-colors shrink-0 shadow-xs"
            aria-label="Send message"
          >
            <Send className="w-3.5 h-3.5" />
          </button>
        </form>
      </div>
    </div>
  );
};
