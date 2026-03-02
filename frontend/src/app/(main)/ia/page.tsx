"use client"

import { useState, useRef, useEffect } from "react"
import { Bot, Send, Loader2, Truck, Sparkles } from "lucide-react"

interface Message {
    role: "user" | "assistant"
    content: string
    timestamp: Date
}

const SUGGESTED_QUESTIONS = [
    "¿Cuál fue el viaje más rentable del mes?",
    "¿Cuánto tenemos en cuentas por cobrar vencidas?",
    "¿Cuál es el rendimiento de diesel de la flota?",
    "Dame un resumen ejecutivo de la operación de febrero",
    "¿Qué operador tiene más viajes completados?",
]

export default function IAPage() {
    const [messages, setMessages] = useState<Message[]>([
        {
            role: "assistant",
            content: "¡Hola! Soy el asistente de inteligencia artificial de **Soluciones-TMS**. Tengo acceso a los datos operativos del sistema: viajes, facturas, flota, diesel e inventario.\n\n¿En qué puedo ayudarte hoy?",
            timestamp: new Date(),
        },
    ])
    const [input, setInput] = useState("")
    const [loading, setLoading] = useState(false)
    const bottomRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" })
    }, [messages])

    async function sendMessage(text: string) {
        if (!text.trim() || loading) return
        const userMsg: Message = { role: "user", content: text, timestamp: new Date() }
        setMessages(m => [...m, userMsg])
        setInput("")
        setLoading(true)

        try {
            const res = await fetch("http://localhost:8001/api/v1/ai/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${localStorage.getItem("token")}`,
                },
                body: JSON.stringify({ message: text }),
            })

            if (res.ok) {
                const data = await res.json()
                setMessages(m => [...m, { role: "assistant", content: data.response, timestamp: new Date() }])
            } else {
                throw new Error("Backend error")
            }
        } catch (e: any) {
            setMessages(m => [
                ...m,
                {
                    role: "assistant",
                    content: "❌ Error de conexión con la Inteligencia Artificial. Por favor asegúrese de tener la API Key de OpenRouter configurada en su servidor o backend. Detalle: " + (e.message || e.toString()),
                    timestamp: new Date()
                }
            ])
            setLoading(false)
            return
        }

        setLoading(false)
    }

    function formatContent(content: string) {
        return content
            .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
            .replace(/\n/g, "<br>")
    }

    return (
        <div className="flex flex-col h-[calc(100vh-8rem)]">
            <div className="mb-4">
                <p className="text-xs text-muted-foreground uppercase tracking-widest font-medium">Inteligencia Artificial</p>
                <h1 className="text-2xl font-semibold tracking-tight mt-0.5 flex items-center gap-2">
                    <Sparkles className="h-5 w-5" />
                    Asistente IA
                </h1>
            </div>

            <div className="flex-1 overflow-y-auto space-y-4 pb-4">
                {messages.map((msg, i) => (
                    <div key={i} className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                        {msg.role === "assistant" && (
                            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-foreground mt-1">
                                <Bot className="h-4 w-4 text-background" />
                            </div>
                        )}
                        <div className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${msg.role === "user"
                            ? "bg-foreground text-background rounded-tr-sm"
                            : "bg-card border border-border rounded-tl-sm"
                            }`}>
                            <div
                                dangerouslySetInnerHTML={{ __html: formatContent(msg.content) }}
                                className="[&_strong]:font-semibold [&_table]:my-2 [&_table]:text-xs [&_td]:pr-4 [&_th]:pr-4 [&_th]:pb-1 [&_th]:text-muted-foreground [&_tbody_tr]:border-t [&_tbody_tr]:border-border"
                            />
                            <div className={`text-xs mt-1.5 ${msg.role === "user" ? "text-background/60 text-right" : "text-muted-foreground"}`}>
                                {msg.timestamp.toLocaleTimeString("es-MX", { hour: "2-digit", minute: "2-digit" })}
                            </div>
                        </div>
                        {msg.role === "user" && (
                            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-muted mt-1">
                                <Truck className="h-4 w-4 text-muted-foreground" />
                            </div>
                        )}
                    </div>
                ))}

                {loading && (
                    <div className="flex gap-3 justify-start">
                        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-foreground mt-1">
                            <Bot className="h-4 w-4 text-background" />
                        </div>
                        <div className="bg-card border border-border rounded-2xl rounded-tl-sm px-4 py-3">
                            <div className="flex items-center gap-1.5">
                                <Loader2 className="h-3.5 w-3.5 animate-spin text-muted-foreground" />
                                <span className="text-sm text-muted-foreground">Analizando datos...</span>
                            </div>
                        </div>
                    </div>
                )}
                <div ref={bottomRef} />
            </div>

            {/* Suggestions */}
            {messages.length <= 1 && (
                <div className="flex flex-wrap gap-2 mb-3">
                    {SUGGESTED_QUESTIONS.map(q => (
                        <button
                            key={q}
                            onClick={() => sendMessage(q)}
                            className="text-xs px-3 py-1.5 rounded-full border border-border bg-muted/30 text-muted-foreground hover:text-foreground hover:border-foreground/30 transition-colors"
                        >
                            {q}
                        </button>
                    ))}
                </div>
            )}

            {/* Input */}
            <div className="flex gap-2">
                <input
                    type="text"
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    onKeyDown={e => e.key === "Enter" && !e.shiftKey && sendMessage(input)}
                    placeholder="Pregúntame sobre la operación, finanzas, flota o rendimientos..."
                    className="flex-1 rounded-xl border border-input bg-card px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring transition-colors"
                />
                <button
                    onClick={() => sendMessage(input)}
                    disabled={!input.trim() || loading}
                    className="flex items-center justify-center rounded-xl bg-foreground px-4 py-2.5 text-background hover:bg-foreground/90 disabled:opacity-40 transition-all"
                >
                    <Send className="h-4 w-4" />
                </button>
            </div>
        </div>
    )
}
