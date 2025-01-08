import React from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { useChatStore } from "@/utils/chat-store";
import brain from "brain";
import { toast } from "sonner";

function CandidateForm() {
  const [name, setName] = React.useState("");
  const [position, setPosition] = React.useState("");
  const [experienceYears, setExperienceYears] = React.useState("");
  const [techStack, setTechStack] = React.useState("");
  const { setCandidateInfo, startInterview } = useChatStore();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !position || !experienceYears || !techStack) {
      toast.error("Please fill in all fields");
      return;
    }

    setCandidateInfo({
      name,
      position,
      experienceYears: parseInt(experienceYears),
      techStack: techStack.split(",").map(tech => tech.trim())
    });
    startInterview();
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="name">Full Name</Label>
        <Input
          id="name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="John Doe"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="position">Position Applied For</Label>
        <Input
          id="position"
          value={position}
          onChange={(e) => setPosition(e.target.value)}
          placeholder="Senior Frontend Developer"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="experience">Years of Experience</Label>
        <Input
          id="experience"
          type="number"
          value={experienceYears}
          onChange={(e) => setExperienceYears(e.target.value)}
          placeholder="5"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="techStack">Tech Stack (comma-separated)</Label>
        <Input
          id="techStack"
          value={techStack}
          onChange={(e) => setTechStack(e.target.value)}
          placeholder="React, TypeScript, Node.js"
        />
      </div>
      <Button type="submit" className="w-full">Start Interview</Button>
    </form>
  );
}

function ChatInterface() {
  const { messages, candidateInfo, addMessage } = useChatStore();
  const [input, setInput] = React.useState("");
  const scrollRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    if (messages.length === 0 && candidateInfo) {
      handleInitialMessage();
    }
  }, [candidateInfo]);

  React.useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleInitialMessage = async () => {
    try {
      const response = await brain.chat({
        candidate_info: {
          name: candidateInfo!.name,
          experience_years: candidateInfo!.experienceYears,
          tech_stack: candidateInfo!.techStack,
          position: candidateInfo!.position
        },
        messages: []
      });
      const data = await response.json();
      addMessage({ role: "assistant", content: data.message });
    } catch (error) {
      toast.error("Failed to start interview");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { role: "user" as const, content: input };
    addMessage(userMessage);
    setInput("");

    try {
      const response = await brain.chat({
        candidate_info: {
          name: candidateInfo!.name,
          experience_years: candidateInfo!.experienceYears,
          tech_stack: candidateInfo!.techStack,
          position: candidateInfo!.position
        },
        messages: [...messages, userMessage]
      });
      const data = await response.json();
      addMessage({ role: "assistant", content: data.message });
    } catch (error) {
      toast.error("Failed to send message");
    }
  };

  return (
    <div className="flex flex-col h-[600px]">
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4">
          {messages.map((message, i) => (
            <div
              key={i}
              className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[80%] rounded-lg p-3 ${message.role === "user" 
                  ? "bg-primary text-primary-foreground" 
                  : "bg-muted"}`}
              >
                {message.content}
              </div>
            </div>
          ))}
          <div ref={scrollRef} />
        </div>
      </ScrollArea>
      <Separator />
      <form onSubmit={handleSubmit} className="p-4">
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your response..."
          />
          <Button type="submit">Send</Button>
        </div>
      </form>
    </div>
  );
}

export default function App() {
  const { isInterviewStarted } = useChatStore();

  return (
    <div className="flex items-center justify-center min-h-screen bg-background">
      <main className="container mx-auto px-4 py-8">
        <Card className="max-w-2xl mx-auto">
          <div className="p-6">
            <h1 className="text-2xl font-bold text-center mb-6">Talent Scout Interview</h1>
            {!isInterviewStarted ? <CandidateForm /> : <ChatInterface />}
          </div>
        </Card>
      </main>
    </div>
  );
}
