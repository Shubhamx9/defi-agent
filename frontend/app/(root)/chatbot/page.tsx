'use client';

import React, { useEffect, useRef, useState } from 'react';
import { Bot, MessageSquare, Moon, Send, Sun } from 'lucide-react';
import { useRecoilState } from 'recoil';
import { darkModeState } from '@/recoil/blackandwhite';
import { SidebarTrigger } from '@/components/ui/sidebar';
import { SignedIn, SignedOut, SignInButton, UserButton, useUser } from '@clerk/nextjs';
import axios from 'axios';

type Role = 'user' | 'bot';
type Message = { role: Role; text: string };

export default function ChatbotPage(): JSX.Element {
  const user = useUser();
  const [darkMode, setDarkMode] = useRecoilState(darkModeState);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (textareaRef.current) {
      autoResize(textareaRef.current);
    }
  }, []);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  function autoResize(el: HTMLTextAreaElement) {
    el.style.height = 'auto';
    const max = 200;
    const newHeight = Math.min(el.scrollHeight, max);
    el.style.height = `${newHeight}px`;
    el.style.overflowY = el.scrollHeight > max ? 'auto' : 'hidden';
  }

  const handleSend = async () => {
  const text = input.trim();
  if (!text) return;

  // Add user message
  const newMessage: Message = { role: 'user', text };
  setMessages(prev => [...prev, newMessage]);
  setInput('');
  if (textareaRef.current) textareaRef.current.style.height = 'auto';

  // Add placeholder bot message (empty, will stream text into it)
  setMessages(prev => [...prev, { role: 'bot', text: '' }]);

  try {
    const eventSource = new EventSource(`http://localhost:8000/chat?query=${encodeURIComponent(text)}&user_id=user_12345&new_chat=${messages.length === 0}`);

    eventSource.onmessage = (event) => {
      if (event.data === "[DONE]") {
        eventSource.close();
        return;
      }

      // Append streamed text to last bot message
      setMessages(prev => {
        const lastMsg = prev[prev.length - 1];
        if (lastMsg.role === 'bot') {
          return [...prev.slice(0, -1), { role: 'bot', text: lastMsg.text + " " + event.data }];
        }
        return prev;
      });
    };

    eventSource.onerror = (err) => {
      console.error("SSE Error:", err);
      setMessages(prev => [
        ...prev.slice(0, -1),
        { role: 'bot', text: '⚠️ Error streaming response.' }
      ]);
      eventSource.close();
    };

  } catch (error) {
    console.error(error);
    setMessages(prev => [
      ...prev.slice(0, -1),
      { role: 'bot', text: '⚠️ Error contacting server.' }
    ]);
  }
};


  return (
    <main className={`h-full w-full flex flex-col ${darkMode ? 'bg-gray-900 text-white' : 'bg-slate-100 text-black'}`}>
      {/* Header */}
      <div className={`border-b ${darkMode ? "border-gray-700" : "border-gray-200"} px-4 py-6 flex justify-between `}>
        <div className={` flex items-center gap-2 sm:gap-4 w-full sm:w-auto justify-center sm:justify-start`}>
            <div className={`rounded-lg ${darkMode ? "bg-gray-900 text-white shadow-gray-500" : "bg-white text-gray-700"} p-1 sm:p-2 shadow-sm`}>
              <MessageSquare className="w-5 h-5 sm:w-6 sm:h-6 text-[#60a5fa]" />
            </div>
            <div>
              <h1 className={`${darkMode? "text-slate-100":"text-gray-700"} text-base sm:text-lg font-semibold tracking-tight`}>
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
              className={`cursor-pointer p-1 sm:p-2 rounded-full border ${darkMode ? "border-gray-600" : "border-gray-400"}`}
              aria-label="Toggle dark mode"
            >
              {darkMode ? <Sun className="w-4 h-4 sm:w-5 sm:h-5 text-yellow-400" /> : <Moon className="w-4 h-4 sm:w-5 sm:h-5 text-gray-700" />}
            </button>
            <button className={`cursor-pointer text-slate-100 bg-gradient-to-r from-blue-500 to-purple-600 shadow hover:scale-105 px-2 sm:px-4 py-1 sm:py-2 rounded-lg hover:bg-blue-700 text-xs sm:text-base font-medium transition-all duration-200`}>
              Connect Wallet 
            </button>
          </div>
      </div>

      {/* Empty State */}
      {messages.length === 0 && (
        <div className="flex-1 flex flex-col items-center justify-center text-center p-6">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-4">Welcome to AI Chatbot</h1>
          <p className={`text-lg max-w-lg ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Ask me anything about crypto, markets, or insights. Start chatting below.</p>
        </div>
      )}

      {/* Chat Messages */}
      {messages.length > 0 && (
        <div className="flex-1 p-6 overflow-y-auto space-y-5">
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-xl px-5 py-3 whitespace-pre-wrap rounded-2xl text-sm shadow-md ${msg.role === 'user' ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-br-none' : darkMode ? 'bg-gray-800 text-gray-200 rounded-bl-none' : 'bg-gray-100 text-gray-800 rounded-bl-none'}`}>
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
          onKeyDown={e => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
        />
        <button type="submit" className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-5 rounded-xl shadow-md hover:scale-105 transform transition flex items-center gap-2">
          <Send className="w-5 h-5" />
        </button>
      </form>
    </main>
  );
}
