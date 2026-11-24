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
  Trash2, 
  Cpu, 
  Plus, 
  Search, 
  Pin, 
  MessageSquare, 
  ArrowDown, 
  Edit2, 
  StopCircle, 
  Volume2
} from 'lucide-react';

interface ConversationItem {
  conversation_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  last_message_at: string;
  archived: boolean;
  pinned: boolean;
  preview: string;
  message_count: number;
}

interface HanaWorkspaceProps {
  currentSessionId: string;
  onSelectSession: (sessionId: string) => void;
  onItineraryUpdated?: (itinerary: ItineraryPlan) => void;
  onProfileUpdated?: (profile: any) => void;
  activeModel?: string;
  externalPrompt?: string;
}

export const HanaWorkspace: React.FC<HanaWorkspaceProps> = ({
  currentSessionId,
  onSelectSession,
  onItineraryUpdated,
  onProfileUpdated,
  activeModel = 'gpt-4o-mini',
  externalPrompt
}) => {
  // Conversation List State
  const [conversations, setConversations] = useState<ConversationItem[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [editingConvId, setEditingConvId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');

  // Active Chat State
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [_lastUserPrompt, setLastUserPrompt] = useState<string>('');
  const [showScrollBottom, setShowScrollBottom] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);

  // References
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const lastExternalPromptRef = useRef<string | null>(null);

  // 1. Fetch Conversations List
  const fetchConversations = async () => {
    try {
      const q = searchQuery.trim() ? `?q=${encodeURIComponent(searchQuery.trim())}` : '';
      const res = await fetch(apiUrl(`/api/v1/conversations${q}`));
      if (res.ok) {
        const data = await res.json();
        setConversations(data.items || []);
      }
    } catch (_) {}
  };

  useEffect(() => {
    fetchConversations();
  }, [searchQuery, currentSessionId]);

  // 2. Load Messages for Active Conversation
  useEffect(() => {
    const loadMessages = async () => {
      try {
        const res = await fetch(apiUrl(`/api/v1/conversations/${currentSessionId}/messages`));
        if (res.ok) {
          const data = await res.json();
          if (data.messages && data.messages.length > 0) {
            setMessages(data.messages);
            return;
          }
        }
      } catch (_) {}

      // Default welcome if no existing messages
      setMessages([
        {
          id: 'welcome',
          sender: 'hana',
          text: "Konnichiwa! I am Hana (ハナ), your AI travel companion for Mount Fuji and the Fuji Five Lakes. I can answer any general question (including Japanese culture, machine learning, technology, translations, and regional weather) or generate personalized multi-day itineraries with verified public transport schedules. How can I assist you today?",
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    };

    loadMessages();
  }, [currentSessionId]);

  // 3. Scroll Management
  const handleScroll = () => {
    if (!messagesContainerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = messagesContainerRef.current;
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 60;
    setShowScrollBottom(!isAtBottom);
  };

  const scrollToBottom = (behavior: ScrollBehavior = 'smooth') => {
    messagesEndRef.current?.scrollIntoView({ behavior });
  };

  useEffect(() => {
    if (!showScrollBottom) {
      scrollToBottom('smooth');
    }
  }, [messages, isStreaming]);

  // 4. External Prompt Triggers
  useEffect(() => {
    if (externalPrompt && externalPrompt !== lastExternalPromptRef.current && !isStreaming) {
      lastExternalPromptRef.current = externalPrompt;
      sendMessage(externalPrompt);
    }
  }, [externalPrompt]);

  // 5. Send Message via Backend SSE
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

    const abortCtrl = new AbortController();
    abortControllerRef.current = abortCtrl;

    try {
      let response = await fetch(apiUrl('/api/v1/chat/stream'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: currentSessionId,
          message: textToSend
        }),
        signal: abortCtrl.signal
      });

      if (!response.ok || !response.body) {
        response = await fetch(apiUrl('/api/ai/chat'), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_id: currentSessionId,
            message: textToSend
          }),
          signal: abortCtrl.signal
        });
      }

      if (!response.ok || !response.body) {
        throw new Error(`HTTP error ${response.status}`);
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
            } catch (_) {}
          } else if (eventType === 'itinerary') {
            try {
              const itineraryData: ItineraryPlan = JSON.parse(eventData);
              if (onItineraryUpdated) onItineraryUpdated(itineraryData);
            } catch (_) {}
          } else if (eventType === 'places') {
            try {
              const places: Place[] = JSON.parse(eventData);
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === hanaMsgId ? { ...m, places } : m
                )
              );
            } catch (_) {}
          } else if (eventType === 'transit') {
            try {
              const journeys: Journey[] = JSON.parse(eventData);
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === hanaMsgId ? { ...m, journeys } : m
                )
              );
            } catch (_) {}
          } else if (eventType === 'crowd_alternatives') {
            try {
              const crowd_alternatives: CrowdAlternativeCard[] = JSON.parse(eventData);
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === hanaMsgId ? { ...m, crowd_alternatives } : m
                )
              );
            } catch (_) {}
          } else if (eventType === 'done') {
            try {
              const doneData = JSON.parse(eventData);
              if (onProfileUpdated && doneData.profile) onProfileUpdated(doneData.profile);
              fetchConversations();
            } catch (_) {}
          }
        }
      }
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === hanaMsgId
              ? { ...m, text: m.text ? `${m.text}\n\n[Communication notice: ${err.message}]` : `[Error: ${err.message}]` }
              : m
          )
        );
      }
    } finally {
      setIsStreaming(false);
      abortControllerRef.current = null;
      fetchConversations();
    }
  };

  const handleStopStreaming = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsStreaming(false);
    }
  };

  const handleNewConversation = async () => {
    const newId = `fn_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`;
    try {
      await fetch(apiUrl('/api/v1/conversations'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: newId, title: 'New Conversation' })
      });
    } catch (_) {}
    onSelectSession(newId);
  };

  const handleSaveTitle = async (convId: string) => {
    if (!editTitle.trim()) {
      setEditingConvId(null);
      return;
    }
    try {
      await fetch(apiUrl(`/api/v1/conversations/${convId}`), {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: editTitle.trim() })
      });
      fetchConversations();
    } catch (_) {}
    setEditingConvId(null);
  };

  const handleTogglePin = async (conv: ConversationItem, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await fetch(apiUrl(`/api/v1/conversations/${conv.conversation_id}`), {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pinned: !conv.pinned })
      });
      fetchConversations();
    } catch (_) {}
  };

  const handleDeleteConversation = async (convId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await fetch(apiUrl(`/api/v1/conversations/${convId}`), { method: 'DELETE' });
      fetchConversations();
      if (convId === currentSessionId) {
        handleNewConversation();
      }
    } catch (_) {}
  };

  const handleCopyText = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleSpeakText = (text: string) => {
    if ('speechSynthesis' in window) {
      if (isSpeaking) {
        window.speechSynthesis.cancel();
        setIsSpeaking(false);
        return;
      }
      const clean = text.replace(/[*_#`]/g, '');
      const utterance = new SpeechSynthesisUtterance(clean);
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);
      window.speechSynthesis.speak(utterance);
      setIsSpeaking(true);
    }
  };

  const quickPrompts = [
    "What is the difference between machine learning and deep learning?",
    "Explain Japanese Omotenashi hospitality & culture",
    "Can you recommend a 1-day itinerary with best Fuji views?",
    "Explain the RAPTOR public transit algorithm in FujiNova",
    "How do I travel from Tokyo to Lake Kawaguchiko?",
    "What is the weather and visibility like in December?"
  ];

  const renderMessageContent = (content: string) => {
    return (
      <div className="whitespace-pre-wrap leading-relaxed space-y-1">
        {content.split('\n').map((line, idx) => {
          const parts = line.split(/(\*\*.*?\*\*)/g);
          return (
            <p key={idx} className={line.startsWith('- ') || line.startsWith('* ') ? 'pl-2 text-slate-200' : ''}>
              {parts.map((part, pIdx) => {
                if (part.startsWith('**') && part.endsWith('**')) {
                  return (
                    <strong key={pIdx} className="font-semibold text-white">
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
    <div className="h-full flex flex-col md:flex-row bg-slate-950 text-white overflow-hidden">
      {/* 1. Left Sidebar: Persistent Chat History */}
      <aside className="w-full md:w-72 lg:w-80 shrink-0 bg-slate-900 border-r border-slate-800 flex flex-col h-48 md:h-full">
        {/* New Chat Button & Search */}
        <div className="p-3 border-b border-slate-800 space-y-2">
          <button
            onClick={handleNewConversation}
            className="w-full flex items-center justify-center gap-2 py-2 px-3 bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 text-white text-xs font-bold rounded-xl shadow-md transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>New Conversation</span>
          </button>

          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search chat history..."
              className="w-full bg-slate-800/80 border border-slate-700/80 text-xs rounded-lg pl-8 pr-3 py-1.5 text-white placeholder:text-slate-500 focus:outline-none focus:border-sky-500"
            />
          </div>
        </div>

        {/* Scrollable Conversations List */}
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {conversations.length === 0 ? (
            <div className="p-4 text-center text-xs text-slate-500">
              No saved conversations yet.
            </div>
          ) : (
            conversations.map((conv) => {
              const isSelected = conv.conversation_id === currentSessionId;
              const isEditing = editingConvId === conv.conversation_id;

              return (
                <div
                  key={conv.conversation_id}
                  onClick={() => onSelectSession(conv.conversation_id)}
                  className={`group relative flex items-center justify-between p-2.5 rounded-xl cursor-pointer text-xs transition-all ${
                    isSelected
                      ? 'bg-slate-800 border border-slate-700 text-white shadow-xs'
                      : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
                  }`}
                >
                  <div className="flex items-center gap-2 min-w-0 flex-1">
                    <MessageSquare className={`w-3.5 h-3.5 shrink-0 ${isSelected ? 'text-sky-400' : 'text-slate-500'}`} />
                    {isEditing ? (
                      <input
                        type="text"
                        value={editTitle}
                        onChange={(e) => setEditTitle(e.target.value)}
                        onBlur={() => handleSaveTitle(conv.conversation_id)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSaveTitle(conv.conversation_id)}
                        autoFocus
                        className="bg-slate-950 border border-sky-500 px-1 py-0.5 rounded text-white text-xs w-full focus:outline-none"
                        onClick={(e) => e.stopPropagation()}
                      />
                    ) : (
                      <div className="truncate">
                        <span className="font-semibold block truncate leading-tight">
                          {conv.title}
                        </span>
                        {conv.preview && (
                          <span className="text-[10px] text-slate-500 block truncate">
                            {conv.preview}
                          </span>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Actions on hover / active */}
                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity ml-1 shrink-0">
                    <button
                      onClick={(e) => handleTogglePin(conv, e)}
                      title={conv.pinned ? 'Unpin' : 'Pin conversation'}
                      className={`p-1 rounded hover:bg-slate-700 ${conv.pinned ? 'text-amber-400' : 'text-slate-500'}`}
                    >
                      <Pin className="w-3 h-3" />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setEditingConvId(conv.conversation_id);
                        setEditTitle(conv.title);
                      }}
                      title="Rename"
                      className="p-1 text-slate-500 hover:text-slate-200 hover:bg-slate-700 rounded"
                    >
                      <Edit2 className="w-3 h-3" />
                    </button>
                    <button
                      onClick={(e) => handleDeleteConversation(conv.conversation_id, e)}
                      title="Delete"
                      className="p-1 text-slate-500 hover:text-rose-400 hover:bg-slate-700 rounded"
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </aside>

      {/* 2. Main ChatGPT-grade Conversation Workspace */}
      <main className="flex-1 flex flex-col h-full bg-slate-950 relative min-w-0">
        {/* Fixed Header */}
        <div className="p-3 border-b border-slate-800 bg-slate-900/80 backdrop-blur-md flex items-center justify-between shrink-0 z-10">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-sky-600 text-white flex items-center justify-center font-bold text-xs shadow-xs">
              ハ
            </div>
            <div>
              <h2 className="text-xs font-bold text-white flex items-center gap-1.5">
                <span>Guide Hana (ハナ)</span>
                <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block animate-pulse" title="Live OpenAI Stream" />
              </h2>
              <p className="text-[10px] text-slate-400">Unrestricted Conversational Tourism & Technology Assistant</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1 text-[10px] text-sky-300 bg-sky-500/10 border border-sky-500/30 px-2 py-0.5 rounded-lg font-mono">
              <Cpu className="w-3 h-3 text-sky-400" />
              <span>{activeModel}</span>
            </div>
          </div>
        </div>

        {/* Scrollable Messages Container with correct nested flexbox min-h-0 */}
        <div 
          ref={messagesContainerRef}
          onScroll={handleScroll}
          className="flex-1 min-h-0 overflow-y-auto p-4 md:p-6 space-y-4"
        >
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex gap-3 max-w-4xl mx-auto ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {msg.sender === 'hana' && (
                <div className="w-7 h-7 rounded-full bg-sky-600 text-white flex items-center justify-center text-xs shrink-0 mt-1 shadow-xs">
                  <Bot className="w-4 h-4" />
                </div>
              )}

              <div className={`max-w-[85%] rounded-2xl px-4 py-3 text-xs sm:text-sm relative group shadow-sm ${
                msg.sender === 'user'
                  ? 'bg-sky-600 text-white rounded-br-xs'
                  : 'bg-slate-900 border border-slate-800 text-slate-200 rounded-bl-xs'
              }`}>
                {/* Assistant message action buttons */}
                {msg.sender === 'hana' && msg.text && (
                  <div className="absolute right-2 top-2 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={() => handleSpeakText(msg.text)}
                      className="p-1 text-slate-400 hover:text-white rounded bg-slate-800"
                      title="Read aloud"
                    >
                      <Volume2 className={`w-3.5 h-3.5 ${isSpeaking ? 'text-sky-400' : ''}`} />
                    </button>
                    <button
                      onClick={() => handleCopyText(msg.id, msg.text)}
                      className="p-1 text-slate-400 hover:text-white rounded bg-slate-800"
                      title="Copy response"
                    >
                      {copiedId === msg.id ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                    </button>
                  </div>
                )}

                {renderMessageContent(msg.text)}

                {/* Verified Transit Connections */}
                {msg.journeys && msg.journeys.length > 0 && (
                  <div className="mt-3">
                    <div className="text-xs font-semibold text-slate-400 flex items-center gap-1 mb-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-sky-400" />
                      <span>Verified Transit Timetables (RAPTOR):</span>
                    </div>
                    <JourneyDisplay journeys={msg.journeys} />
                  </div>
                )}

                {/* CrowdSense Quieter Alternatives */}
                {msg.crowd_alternatives && msg.crowd_alternatives.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-slate-800 space-y-2">
                    <div className="text-xs font-semibold text-emerald-400 flex items-center gap-1">
                      <Users className="w-3.5 h-3.5" />
                      <span>CrowdSense Quieter Alternatives:</span>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {msg.crowd_alternatives.map((alt) => (
                        <div
                          key={alt.place_id}
                          className="bg-slate-800/80 border border-emerald-500/30 rounded-xl p-2.5 flex items-center gap-2.5"
                        >
                          <img
                            src={alt.image_url}
                            alt={alt.name_en}
                            className="w-12 h-12 rounded-lg object-cover bg-slate-700 shrink-0"
                          />
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between gap-1">
                              <h4 className="text-xs font-bold text-white truncate">{alt.name_en}</h4>
                              <span className="text-[10px] font-bold text-emerald-300 bg-emerald-500/20 border border-emerald-500/30 px-1.5 py-0.5 rounded-full shrink-0">
                                -{alt.crowd_reduction_percent}%
                              </span>
                            </div>
                            <p className="text-[10px] text-slate-400 truncate">{alt.name_ja}</p>
                            <p className="text-[10px] text-slate-300 line-clamp-1">{alt.recommendation_reason}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Recommended Place Cards */}
                {msg.places && msg.places.length > 0 && (
                  <div className="mt-3 space-y-2 pt-3 border-t border-slate-800">
                    <div className="text-xs font-semibold text-amber-400 flex items-center gap-1">
                      <Sparkles className="w-3.5 h-3.5" />
                      <span>Verified Destination Recommendations:</span>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {msg.places.map((place) => (
                        <PlaceCard key={place.place_id} place={place} />
                      ))}
                    </div>
                  </div>
                )}

                <span className={`block text-[10px] mt-1.5 ${
                  msg.sender === 'user' ? 'text-sky-200 text-right' : 'text-slate-500'
                }`}>
                  {msg.timestamp}
                </span>
              </div>

              {msg.sender === 'user' && (
                <div className="w-7 h-7 rounded-full bg-slate-700 text-slate-200 flex items-center justify-center text-xs shrink-0 mt-1">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          ))}

          {isStreaming && (
            <div className="max-w-4xl mx-auto flex items-center gap-2 text-xs text-sky-400 italic">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Hana is thinking and consulting verified knowledge...</span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Scroll-to-Bottom Floating Pill */}
        {showScrollBottom && (
          <button
            onClick={() => scrollToBottom('smooth')}
            className="absolute bottom-28 right-8 p-2 rounded-full bg-sky-600 text-white shadow-xl hover:bg-sky-500 transition-all z-20"
            title="Scroll to latest messages"
          >
            <ArrowDown className="w-4 h-4" />
          </button>
        )}

        {/* Fixed Bottom Composer Area */}
        <div className="p-3 md:p-4 border-t border-slate-800 bg-slate-900 shrink-0">
          <div className="max-w-4xl mx-auto space-y-2">
            {/* Quick Prompt Carousel */}
            <div className="flex items-center gap-1.5 overflow-x-auto text-[11px] pb-1">
              <span className="text-[10px] font-semibold text-slate-500 shrink-0">Try:</span>
              {quickPrompts.map((p, idx) => (
                <button
                  key={idx}
                  onClick={() => sendMessage(p)}
                  disabled={isStreaming}
                  className="shrink-0 px-2.5 py-1 rounded-full bg-slate-800 border border-slate-700 text-slate-300 hover:border-sky-500 hover:text-white transition-colors disabled:opacity-50"
                >
                  {p}
                </button>
              ))}
            </div>

            {/* Input Composer Form */}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                sendMessage();
              }}
              className="relative flex items-end gap-2 bg-slate-950 border border-slate-800 rounded-2xl p-2 focus-within:border-sky-500 focus-within:ring-1 focus-within:ring-sky-500/30 transition-all"
            >
              <textarea
                ref={textareaRef}
                rows={1}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                  }
                }}
                placeholder="Ask Hana anything (Shift+Enter for newline)..."
                disabled={isStreaming}
                className="flex-1 bg-transparent border-none text-xs sm:text-sm text-white px-3 py-1.5 focus:outline-none resize-none max-h-32 placeholder:text-slate-500 leading-relaxed"
              />

              {isStreaming ? (
                <button
                  type="button"
                  onClick={handleStopStreaming}
                  className="p-2.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white transition-colors shrink-0"
                  title="Stop generation"
                >
                  <StopCircle className="w-4 h-4" />
                </button>
              ) : (
                <button
                  type="submit"
                  disabled={!input.trim()}
                  className="p-2.5 rounded-xl bg-sky-600 hover:bg-sky-500 disabled:opacity-40 text-white transition-colors shrink-0 shadow-xs"
                  aria-label="Send message"
                >
                  <Send className="w-4 h-4" />
                </button>
              )}
            </form>
          </div>
        </div>
      </main>
    </div>
  );
};
