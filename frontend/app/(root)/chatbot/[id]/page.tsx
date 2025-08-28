// app/chatbot/[id]/page.tsx
'use client';

import React, { useEffect, useRef, useState } from 'react';
import { MessageSquare, Moon, Send, Sun, Plus } from 'lucide-react';
import { useRecoilState } from 'recoil';
import { darkModeState } from '@/recoil/blackandwhite';
import { useUser } from '@clerk/nextjs';
import WalletButton from '@/components/ui/connect-wallet';
import Providers from '@/components/Providers';
import { useRouter, useParams } from 'next/navigation';

type Role = 'user' | 'bot';
type Message = { role: Role; text: string; id?: string };

const LOCAL_KEY = 'chat_session_id';

export default function ChatbotPage(): JSX.Element {
  const user = useUser();
  const [darkMode, setDarkMode] = useRecoilState(darkModeState);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [chatId, setChatId] = useState<string | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const router = useRouter();
  const params = useParams();
  const urlId = params?.id ? String(params.id) : null;

  // Auto-resize textarea
  useEffect(() => { if (textareaRef.current) autoResize(textareaRef.current); }, []);

  // Auto-scroll on new messages
  useEffect(() => { if (messagesEndRef.current) messagesEndRef.current.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

  // Initialization: use URL id (preferred), otherwise fallback to localStorage, otherwise create a new chat
  useEffect(() => {
    (async () => {
      try {
        const local = typeof window !== 'undefined' ? localStorage.getItem(LOCAL_KEY) : null;

        if (urlId) {
          setChatId(urlId);
          localStorage.setItem(LOCAL_KEY, urlId);
          await loadHistory(urlId);
          return;
        }

        if (local) {
          // navigate to stored session
          router.replace(`/chatbot/${local}`);
          return;
        }

        // create new chat if nothing exists
        const res = await fetch('/api/chats', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title: 'New Chat', userId: user.user?.id ?? null }),
        });
        if (!res.ok) throw new Error('Failed to create chat');
        const newChat = await res.json();
        const id = newChat.id as string;
        localStorage.setItem(LOCAL_KEY, id);
        router.replace(`/chatbot/${id}`);
      } catch (err) {
        console.error('Init error', err);
      }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [urlId, user.user?.id]);

  // Load history when chatId changes
  useEffect(() => {
    if (!chatId) return;
    loadHistory(chatId);
  }, [chatId]);

  async function loadHistory(id: string) {
    try {
      const res = await fetch(`/api/chats/${id}/messages`);
      if (!res.ok) throw new Error('Failed to load history');
      const data = await res.json();
      // normalize to { role, text }
      const msgs: Message[] = data.map((m: any) => ({ role: m.role === 'assistant' ? 'bot' : m.role, text: m.content, id: m.id }));
      setMessages(msgs);
      setChatId(id);
    } catch (err) {
      console.error('Failed to load chat history:', err);
    }
  }

  function autoResize(el: HTMLTextAreaElement) {
    el.style.height = 'auto';
    const max = 200;
    const newHeight = Math.min(el.scrollHeight, max);
    el.style.height = `${newHeight}px`;
    el.style.overflowY = el.scrollHeight > max ? 'auto' : 'hidden';
  }

  // KEY FIX: Save user message first, then call AI, then save bot response
  const handleSend = async () => {
    const text = input.trim();
    if (!text) return;
    if (!chatId) {
      console.error('No chat id available.');
      return;
    }

    // Optimistic UI: show user and placeholder bot
    setMessages(prev => [...prev, { role: 'user', text }]);
    setInput('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
    setMessages(prev => [...prev, { role: 'bot', text: '' }]); // placeholder

    try {
      // 1) Save user message to DB
      const saveUser = await fetch(`/api/chats/${chatId}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: text, role: 'user' }),
      });
      if (!saveUser.ok) console.warn('Failed to persist user message');

      // 2) Call AI (FastAPI)
      const res = await fetch('http://localhost:8000/query/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: text,
          user_id: user.user?.id || 'guest_user',
          session_id: chatId,
        }),
      });
      const aiData = await res.json();
      const botText = aiData.answer || aiData.clarification_question || 'No answer.';

      // 3) Replace placeholder in UI with real bot response
      setMessages(prev => {
        // replace last placeholder bot message
        const copy = [...prev];
        for (let i = copy.length - 1; i >= 0; i--) {
          if (copy[i].role === 'bot' && copy[i].text === '') {
            copy[i] = { role: 'bot', text: botText };
            return copy;
          }
        }
        // fallback append
        return [...copy, { role: 'bot', text: botText }];
      });

      // 4) Save bot response to DB
      const saveBot = await fetch(`/api/chats/${chatId}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: botText, role: 'assistant' }),
      });
      if (!saveBot.ok) console.warn('Failed to persist bot message');
    } catch (error) {
      console.error(error);
      setMessages(prev => [
        ...prev.slice(0, -1),
        { role: 'bot', text: '⚠️ Error contacting server.' }
      ]);
    }
  };

  const newChat = async () => {
    try {
      const res = await fetch('/api/chats', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: 'New Chat', userId: user.user?.id ?? null }),
      });
      if (!res.ok) throw new Error('Failed to create chat');
      const created = await res.json();
      const id = created.id as string;
      localStorage.setItem(LOCAL_KEY, id);
      router.replace(`/chatbot/${id}`);
      setMessages([]);
    } catch (err) {
      console.error('Failed to create new chat', err);
    }
  };

  /* ------------------------
     UI (unchanged, only wiring above)
     ------------------------ */
  return (
    <main className={`h-full w-full flex flex-col ${darkMode ? 'bg-gray-900 text-white' : 'bg-slate-100 text-black'}`}>
      {/* Header */}
      <div className={`border-b ${darkMode ? "border-gray-700" : "border-gray-200"} px-4 py-6 flex justify-between`}>
        <div className="flex items-center gap-2 sm:gap-4 w-full sm:w-auto justify-center sm:justify-start">
          <div className={`rounded-lg ${darkMode ? "bg-gray-900 text-white shadow-gray-500" : "bg-white text-gray-700"} p-1 sm:p-2 shadow-sm`}>
            <MessageSquare className="w-5 h-5 sm:w-6 sm:h-6 text-[#60a5fa]" />
          </div>
          <div>
            <h1 className={`${darkMode ? "text-slate-100" : "text-gray-700"} text-base sm:text-lg font-semibold tracking-tight`}>
              DeFi AI Assistant
            </h1>
            <div className="text-[10px] sm:text-xs text-slate-400">
              Powered by <span className="text-[#60a5fa] font-medium">Coinbase</span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2 sm:gap-6 w-full sm:w-auto justify-center sm:justify-end">
          <button
            onClick={() => setDarkMode(!darkMode)}
            className={`cursor-pointer p-2 rounded-full border transition-all hover:scale-110 hover:shadow-[0_0_10px_rgba(250,204,21,0.7)] ${darkMode ? "border-gray-600" : "border-gray-400"}`}
            aria-label="Toggle dark mode"
          >
            {darkMode ? (
              <Sun className="w-5 h-5 text-yellow-400 animate-pulse" />
            ) : (
              <Moon className="w-5 h-5 text-gray-700" />
            )}
          </button>

          {/* New Chat button */}
          <button onClick={newChat} className="flex items-center gap-2 px-3 py-2 rounded-md border hover:shadow-sm" aria-label="New Chat">
            <Plus className="w-4 h-4" />
            <span className="text-sm">New Chat</span>
          </button>

          <Providers>
            <WalletButton />
          </Providers>
        </div>
      </div>

      {/* Empty State */}
      {messages.length === 0 && (
        <div className="flex-1 flex flex-col items-center justify-center text-center p-6">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-4">
            Welcome to AI Chatbot
          </h1>
          <p className={`text-lg max-w-lg ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
            Ask me anything about crypto, markets, or insights. Start chatting below.
          </p>
        </div>
      )}

      {/* Chat Messages */}
      {messages.length > 0 && (
        <div className="flex-1 p-6 overflow-y-auto space-y-5">
          {messages.map((msg, i) => (
            <div key={msg.id ?? i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-xl px-5 py-3 whitespace-pre-wrap rounded-2xl text-sm shadow-md 
                ${msg.role === 'user'
                    ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-br-none'
                    : darkMode
                      ? 'bg-gray-800 text-gray-200 rounded-bl-none'
                      : 'bg-gray-100 text-gray-800 rounded-bl-none'}`}>
                {msg.text}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
      )}

      {/* Input Box */}
      <form onSubmit={e => { e.preventDefault(); handleSend(); }} className={`p-4 border-t ${darkMode ? 'border-gray-800 bg-gray-900' : 'border-gray-200 bg-white'} flex gap-3`}>
        <textarea
          ref={textareaRef}
          value={input}
          onChange={e => { setInput(e.target.value); if (textareaRef.current) autoResize(textareaRef.current); }}
          placeholder="Type your message..."
          className={`flex-1 px-4 py-3 rounded-xl focus:outline-none shadow-sm overflow-hidden ${darkMode ? 'bg-gray-800 text-white placeholder-gray-400' : 'bg-gray-100 text-black placeholder-gray-500'}`}
          rows={1}
          onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); } }}
        />
        <button type="submit" className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-5 rounded-xl shadow-md hover:scale-105 transform transition flex items-center gap-2">
          <Send className="w-5 h-5" />
        </button>
      </form>
    </main>
  );
}
