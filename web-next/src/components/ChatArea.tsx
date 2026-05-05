"use client";
import { useEffect, useRef, useState } from "react";
import { useChat } from "@/context/ChatContext";
import { Message } from "@/lib/api";

function MsgBubble({ 
  msg, idx, isFirstInGroup, isLastInGroup 
}: { 
  msg: Message; idx: number; isFirstInGroup: boolean; isLastInGroup: boolean;
}) {
  const { deleteMessage } = useChat();
  const isUser = msg.role === "user";
  const [hov, setHov] = useState(false);

  let radiusClass = "rounded-[18px]";
  if (isUser) {
    if (isFirstInGroup && !isLastInGroup) radiusClass = "rounded-[18px] rounded-br-[4px]";
    else if (!isFirstInGroup && !isLastInGroup) radiusClass = "rounded-[18px] rounded-tr-[4px] rounded-br-[4px]";
    else if (!isFirstInGroup && isLastInGroup) radiusClass = "rounded-[18px] rounded-tr-[4px]";
  } else {
    if (isFirstInGroup && !isLastInGroup) radiusClass = "rounded-[18px] rounded-bl-[4px]";
    else if (!isFirstInGroup && !isLastInGroup) radiusClass = "rounded-[18px] rounded-tl-[4px] rounded-bl-[4px]";
    else if (!isFirstInGroup && isLastInGroup) radiusClass = "rounded-[18px] rounded-tl-[4px]";
  }

  // Margin logic: tight between group, loose between different groups
  const mbClass = isLastInGroup ? "mb-4" : "mb-[2px]";

  return (
    <div className={`flex flex-col ${isUser ? "items-end" : "items-start"} w-full ${mbClass}`}>
      {/* Name on top of first message in AI group */}
      {isFirstInGroup && !isUser && (
        <span className="text-[11px] font-semibold text-[#8b90a7] ml-[46px] mb-1">AI Assistant</span>
      )}
      
      <div
        className={`flex items-end gap-2 group relative w-full ${isUser ? "flex-row-reverse" : ""}`}
        onMouseEnter={() => setHov(true)}
        onMouseLeave={() => setHov(false)}
      >
        {/* Avatar area (36px width to reserve space even if invisible) */}
        {!isUser && (
          <div className="w-9 h-9 flex-shrink-0 self-end">
            {isLastInGroup && (
              <div className="w-9 h-9 rounded-full bg-[#1e2533] border border-[#4f6ef7] border-[1.5px] flex items-center justify-center text-[#4f6ef7] text-sm font-bold">
                ✦
              </div>
            )}
          </div>
        )}

        {/* Bubble */}
        <div
          className={`max-w-[520px] px-4 py-2.5 text-[15px] leading-relaxed whitespace-pre-wrap break-words
            ${isUser ? "bg-[#4f6ef7] text-white" : "bg-[#1e2533] text-[#e4e6f0]"}
            ${radiusClass}
          `}
        >
          {msg.content}
        </div>

        {/* Delete button */}
        {hov && (
          <button
            onClick={() => deleteMessage(idx)}
            className={`text-[11px] px-1.5 py-0.5 rounded bg-[#2a1a1a] text-red-400 hover:bg-red-900/40 transition-colors self-center flex-shrink-0`}
            title="Xóa tin nhắn"
          >✕</button>
        )}
      </div>
    </div>
  );
}

function DatePill({ text }: { text: string }) {
  return (
    <div className="flex justify-center my-3 mb-6">
      <span className="bg-[#1e2330] text-[#545872] text-[11px] font-semibold px-4 py-1 rounded-xl">{text}</span>
    </div>
  );
}

function WelcomeScreen() {
  return (
    <div className="flex flex-col items-center justify-center flex-1 gap-3 py-20">
      <div className="w-16 h-16 rounded-full bg-[#1e2533] border-[1.5px] border-[#4f6ef7] flex items-center justify-center text-[#4f6ef7] text-3xl">✦</div>
      <h2 className="text-xl font-extrabold text-[#e4e6f0]">AI Assistant</h2>
      <span className="text-xs font-semibold text-[#25d366]">● Active Now</span>
      <p className="text-sm text-[#545872]">Send a message to start chatting</p>
    </div>
  );
}

function TypingIndicator({ isFirstInGroup }: { isFirstInGroup: boolean }) {
  // If it's the first in the group, we show the name
  const radiusClass = isFirstInGroup ? "rounded-[18px] rounded-bl-[4px]" : "rounded-[18px] rounded-tl-[4px] rounded-bl-[4px]";
  
  return (
    <div className={`flex flex-col items-start w-full mb-4`}>
      {isFirstInGroup && (
        <span className="text-[11px] font-semibold text-[#8b90a7] ml-[46px] mb-1">AI Assistant</span>
      )}
      <div className="flex items-end gap-2 w-full">
        <div className="w-9 h-9 flex-shrink-0 self-end">
          <div className="w-9 h-9 rounded-full bg-[#1e2533] border border-[#4f6ef7] border-[1.5px] flex items-center justify-center text-[#4f6ef7] text-sm font-bold">
            ✦
          </div>
        </div>
        <div className={`bg-[#1e2533] ${radiusClass} px-5 py-3 text-[#4f6ef7] text-lg tracking-widest animate-pulse`}>
          ●●●
        </div>
      </div>
    </div>
  );
}

export default function ChatArea() {
  const { messages, sending, activeId } = useChat();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sending]);

  return (
    <div className="flex-1 overflow-y-auto px-5 py-5 flex flex-col scrollbar-thin scrollbar-thumb-[#1e2230]">
      {messages.length === 0 && !sending ? (
        <WelcomeScreen />
      ) : (
        <>
          <DatePill text="Today" />
          {messages.map((msg, i) => {
            const prevMsg = i > 0 ? messages[i - 1] : null;
            const nextMsg = i < messages.length - 1 ? messages[i + 1] : null;
            
            // Group messages if they are consecutive and from the same role
            const isFirstInGroup = !prevMsg || prevMsg.role !== msg.role;
            // A message is the last in its group if there's no next message, 
            // OR if the next message is from a different role. 
            // BUT, if we are 'sending' (typing) and this is an AI message at the very end,
            // the typing indicator will act as the continuation of the group!
            // Wait, if sending is true and we are the last AI message, are we really the last?
            // No, the TypingIndicator will follow us, so we shouldn't show the avatar!
            const isLastInList = i === messages.length - 1;
            const isFollowedByTyping = isLastInList && sending && msg.role === "assistant";
            
            const isLastInGroup = (!nextMsg || nextMsg.role !== msg.role) && !isFollowedByTyping;

            return (
              <MsgBubble 
                key={i} 
                msg={msg} 
                idx={i} 
                isFirstInGroup={isFirstInGroup} 
                isLastInGroup={isLastInGroup} 
              />
            );
          })}
          {sending && (
            <TypingIndicator 
              isFirstInGroup={messages.length === 0 || messages[messages.length - 1].role !== "assistant"} 
            />
          )}
        </>
      )}
      <div ref={bottomRef} />
    </div>
  );
}
