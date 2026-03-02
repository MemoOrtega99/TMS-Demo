"use client"

import { useState, useRef, useEffect, useCallback } from "react"
import { useParams } from "next/navigation"
import {
    ArrowLeft, Truck, MapPin, Calendar, User, Package,
    Receipt, TrendingUp, Clock, CheckCircle,
    AlertTriangle, Send, Wifi, WifiOff
} from "lucide-react"
import Link from "next/link"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"

type TabId = "info" | "tracking" | "gastos" | "rentabilidad"

interface TrackingComment {
    id: number
    tipo: "actualizacion" | "incidencia" | "estatus_change" | "documento"
    mensaje: string
    ubicacion?: string | null
    usuario_id?: number | null
    created_at: string
}

const TRIP_MOCK = {
    numero: "VJ-2026-0018",
    estatus: "en_ruta",
    cliente: "Grupo Bimbo",
    origen: "Altamira, Tamaulipas",
    destino: "Monterrey, Nuevo León",
    distancia_km: 380,
    tipo_carga: "Producto terminado (pan de caja)",
    peso_toneladas: 22.5,
    fecha_programada: "2026-03-01",
    tarifa_cliente: 85000,
    unidad: "ECO-003",
    marca_modelo: "Kenworth T680 2023",
    remolque: "REM-005",
    operador: "J. Martínez Soto",
}

const GASTOS_MOCK = [
    { tipo: "Caseta", descripcion: "Caseta Puente Nacional", monto: 485 },
    { tipo: "Caseta", descripcion: "Caseta Linares", monto: 1250 },
    { tipo: "Combustible", descripcion: "280 litros a $25.50/L", monto: 7140 },
    { tipo: "Viáticos", descripcion: "Viáticos operador — día 1", monto: 500 },
]

const DEMO_TRACKING: TrackingComment[] = [
    { id: 1, tipo: "estatus_change", mensaje: "Viaje programado y listo para asignación", created_at: "2026-03-01T06:00:00Z" },
    { id: 2, tipo: "estatus_change", mensaje: "Unidad ECO-003 asignada. Operador J. Martínez Soto confirmado", ubicacion: "Patio Altamira", created_at: "2026-03-01T07:00:00Z" },
    { id: 3, tipo: "actualizacion", mensaje: "Unidad salió de patio con carga completa (22.5 ton). Todo en orden.", ubicacion: "Patio Altamira, Tam", created_at: "2026-03-01T07:15:00Z" },
    { id: 4, tipo: "actualizacion", mensaje: "Pasé caseta Puente Nacional sin novedad. Continúo ruta.", ubicacion: "Caseta Puente Nacional, Ver", created_at: "2026-03-01T09:30:00Z" },
    { id: 5, tipo: "incidencia", mensaje: "Retraso por revisión federal en caseta Linares. Aprox 45 min de espera.", ubicacion: "Caseta Linares, NL", created_at: "2026-03-01T13:00:00Z" },
    { id: 6, tipo: "actualizacion", mensaje: "Retomé ruta después de revisión. ETA Monterrey 16:30 hrs.", ubicacion: "Caseta Linares, NL", created_at: "2026-03-01T13:45:00Z" },
]

const MXN = (v: number) => new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN", maximumFractionDigits: 0 }).format(v)

const TABS: { id: TabId; label: string; icon: React.ElementType }[] = [
    { id: "tracking", label: "Tracking", icon: MapPin },
    { id: "info", label: "Info General", icon: Package },
    { id: "gastos", label: "Gastos", icon: Receipt },
    { id: "rentabilidad", label: "Rentabilidad", icon: TrendingUp },
]

const statusBadge: Record<string, string> = {
    en_ruta: "bg-blue-500/15 text-blue-400 border-blue-500/30",
    completado: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    programado: "bg-yellow-500/15 text-yellow-400 border-yellow-500/30",
    cancelado: "bg-red-500/15 text-red-400 border-red-500/30",
}

function formatHora(iso: string) {
    return new Date(iso).toLocaleString("es-MX", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })
}

export default function ViajeDetailPage() {
    const params = useParams()
    const tripId = params?.id as string

    const [activeTab, setActiveTab] = useState<TabId>("tracking")
    const [comments, setComments] = useState<TrackingComment[]>(DEMO_TRACKING)
    const [nuevoComentario, setNuevoComentario] = useState("")
    const [ubicacion, setUbicacion] = useState("")
    const [wsStatus, setWsStatus] = useState<"disconnected" | "connecting" | "connected">("disconnected")
    const wsRef = useRef<WebSocket | null>(null)
    const bottomRef = useRef<HTMLDivElement>(null)

    const totalGastos = GASTOS_MOCK.reduce((a, g) => a + g.monto, 0)
    const utilidadBruta = TRIP_MOCK.tarifa_cliente - totalGastos
    const margen = ((utilidadBruta / TRIP_MOCK.tarifa_cliente) * 100).toFixed(1)

    // WebSocket connection
    const connectWS = useCallback(() => {
        // Resolve numeric trip ID from the URL param (VJ-2026-0018 -> look up by numero)
        // For demo we use trip ID = 1 as fallback; real impl would look up from API
        const wsUrl = `ws://localhost:8001/api/v1/ws/trips/${params.id}/tracking`
        setWsStatus("connecting")

        const ws = new WebSocket(wsUrl)
        wsRef.current = ws

        ws.onopen = () => {
            setWsStatus("connected")
        }

        ws.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data)
                if (msg.type === "history") {
                    // Replace mock data with real history from DB
                    if (Array.isArray(msg.data) && msg.data.length > 0) {
                        setComments(msg.data)
                    }
                } else if (msg.type === "comment") {
                    setComments(prev => [...prev, msg.data])
                }
            } catch { }
        }

        ws.onclose = () => {
            setWsStatus("disconnected")
            wsRef.current = null
        }

        ws.onerror = () => {
            // Backend not running — stay with mock data
            setWsStatus("disconnected")
            ws.close()
        }
    }, [])

    useEffect(() => {
        connectWS()
        return () => {
            wsRef.current?.close()
        }
    }, [connectWS])

    // Auto-scroll timeline
    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" })
    }, [comments])

    function enviarComentario() {
        if (!nuevoComentario.trim()) return

        if (wsRef.current?.readyState === WebSocket.OPEN) {
            // Send via WebSocket — backend persists and broadcasts
            wsRef.current.send(JSON.stringify({
                mensaje: nuevoComentario,
                ubicacion: ubicacion || null,
                tipo: "actualizacion",
            }))
        } else {
            // Fallback: add locally (demo mode)
            const nuevo: TrackingComment = {
                id: comments.length + 1,
                tipo: "actualizacion",
                mensaje: nuevoComentario,
                ubicacion: ubicacion || null,
                created_at: new Date().toISOString(),
            }
            setComments(prev => [...prev, nuevo])
        }
        setNuevoComentario("")
        setUbicacion("")
    }

    return (
        <div className="space-y-5">
            {/* Back + Header */}
            <div>
                <Link href="/operaciones/viajes" className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground mb-3 transition-colors w-fit">
                    <ArrowLeft className="h-3 w-3" /> Volver a Viajes
                </Link>
                <div className="flex items-start justify-between gap-4">
                    <div>
                        <p className="text-xs text-muted-foreground uppercase tracking-widest font-medium">Expediente de Viaje</p>
                        <h1 className="text-2xl font-semibold tracking-tight mt-0.5 flex items-center gap-3">
                            {tripId ?? TRIP_MOCK.numero}
                            <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium border ${statusBadge[TRIP_MOCK.estatus]}`}>
                                En Ruta
                            </span>
                        </h1>
                    </div>
                    <div className="text-right shrink-0">
                        <div className="text-xs text-muted-foreground">Tarifa al cliente</div>
                        <div className="text-xl font-bold tabular-nums">{MXN(TRIP_MOCK.tarifa_cliente)}</div>
                    </div>
                </div>

                <div className="flex items-center gap-3 mt-3 text-sm">
                    <div className="flex items-center gap-1.5 text-muted-foreground">
                        <MapPin className="h-4 w-4 text-emerald-400" />
                        <span>{TRIP_MOCK.origen}</span>
                    </div>
                    <div className="flex items-center gap-2 text-muted-foreground/40">
                        <div className="h-px w-8 bg-border" />
                        <ArrowLeft className="h-3 w-3 rotate-180" />
                        <div className="h-px w-8 bg-border" />
                    </div>
                    <div className="flex items-center gap-1.5 text-muted-foreground">
                        <MapPin className="h-4 w-4 text-red-400" />
                        <span>{TRIP_MOCK.destino}</span>
                    </div>
                    <span className="text-xs text-muted-foreground ml-2">· {TRIP_MOCK.distancia_km} km</span>
                </div>
            </div>

            {/* Tabs */}
            <div className="flex gap-1 border-b border-border">
                {TABS.map(tab => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`flex items-center gap-1.5 px-4 py-2.5 text-sm font-medium border-b-2 transition-colors -mb-px ${activeTab === tab.id
                            ? "border-foreground text-foreground"
                            : "border-transparent text-muted-foreground hover:text-foreground"
                            }`}
                    >
                        <tab.icon className="h-3.5 w-3.5" />
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* INFO TAB */}
            {activeTab === "info" && (
                <div className="grid gap-4 md:grid-cols-2">
                    <Card>
                        <CardHeader className="px-5 pt-4 pb-2"><CardTitle className="text-sm font-medium">Asignación</CardTitle></CardHeader>
                        <CardContent className="px-5 pb-5 space-y-3">
                            {[
                                { icon: User, label: "Cliente", value: TRIP_MOCK.cliente },
                                { icon: Truck, label: "Unidad", value: `${TRIP_MOCK.unidad} — ${TRIP_MOCK.marca_modelo}` },
                                { icon: Package, label: "Remolque", value: TRIP_MOCK.remolque },
                                { icon: User, label: "Operador", value: TRIP_MOCK.operador },
                            ].map(item => (
                                <div key={item.label} className="flex items-center gap-3">
                                    <item.icon className="h-4 w-4 text-muted-foreground shrink-0" />
                                    <div>
                                        <div className="text-xs text-muted-foreground">{item.label}</div>
                                        <div className="text-sm font-medium">{item.value}</div>
                                    </div>
                                </div>
                            ))}
                        </CardContent>
                    </Card>
                    <Card>
                        <CardHeader className="px-5 pt-4 pb-2"><CardTitle className="text-sm font-medium">Carga y Fechas</CardTitle></CardHeader>
                        <CardContent className="px-5 pb-5 space-y-3">
                            {[
                                { icon: Package, label: "Tipo de carga", value: TRIP_MOCK.tipo_carga },
                                { icon: Package, label: "Peso", value: `${TRIP_MOCK.peso_toneladas} toneladas` },
                                { icon: Calendar, label: "Fecha programada", value: TRIP_MOCK.fecha_programada },
                                { icon: Clock, label: "Salida real", value: "01 Mar 2026 · 07:15 hrs" },
                            ].map(item => (
                                <div key={item.label} className="flex items-center gap-3">
                                    <item.icon className="h-4 w-4 text-muted-foreground shrink-0" />
                                    <div>
                                        <div className="text-xs text-muted-foreground">{item.label}</div>
                                        <div className="text-sm font-medium">{item.value}</div>
                                    </div>
                                </div>
                            ))}
                        </CardContent>
                    </Card>
                </div>
            )}

            {/* TRACKING TAB */}
            {activeTab === "tracking" && (
                <div className="space-y-4 max-w-2xl">
                    {/* WS status bar */}
                    <div className={`flex items-center gap-2 rounded-md px-3 py-2 text-xs border ${wsStatus === "connected"
                        ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
                        : wsStatus === "connecting"
                            ? "bg-yellow-500/10 text-yellow-400 border-yellow-500/30"
                            : "bg-muted/30 text-muted-foreground border-border"
                        }`}>
                        {wsStatus === "connected"
                            ? <><Wifi className="h-3.5 w-3.5" /> Conectado — actualizaciones en tiempo real activas</>
                            : wsStatus === "connecting"
                                ? <><Wifi className="h-3.5 w-3.5 animate-pulse" /> Conectando al servidor de tracking...</>
                                : <><WifiOff className="h-3.5 w-3.5" /> Modo demo — backend no disponible (datos de ejemplo)</>
                        }
                    </div>

                    <Card>
                        <CardHeader className="px-5 pt-4 pb-2">
                            <CardTitle className="text-sm font-medium">Timeline de Tracking</CardTitle>
                            <CardDescription className="text-xs">{comments.length} actualizaciones</CardDescription>
                        </CardHeader>
                        <CardContent className="px-5 pb-5">
                            <div className="relative">
                                <div className="absolute left-4 top-4 bottom-4 w-px bg-border" />
                                <div className="space-y-5">
                                    {comments.map(entry => (
                                        <div key={entry.id} className="flex gap-4 relative">
                                            <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full border-2 z-10 ${entry.tipo === "incidencia"
                                                ? "bg-yellow-500/15 border-yellow-500/50"
                                                : entry.tipo === "estatus_change"
                                                    ? "bg-emerald-500/15 border-emerald-500/50"
                                                    : "bg-blue-500/15 border-blue-500/50"
                                                }`}>
                                                {entry.tipo === "incidencia"
                                                    ? <AlertTriangle className="h-3.5 w-3.5 text-yellow-400" />
                                                    : entry.tipo === "estatus_change"
                                                        ? <CheckCircle className="h-3.5 w-3.5 text-emerald-400" />
                                                        : <Truck className="h-3.5 w-3.5 text-blue-400" />
                                                }
                                            </div>
                                            <div className="flex-1 pb-1">
                                                <div className="flex items-center justify-between gap-2 mb-0.5">
                                                    <span className="text-xs font-medium text-muted-foreground">
                                                        {entry.tipo === "incidencia" ? "⚠️ Incidencia" : entry.tipo === "estatus_change" ? "Cambio de estatus" : "Actualización"}
                                                    </span>
                                                    <span className="text-xs text-muted-foreground/60">{formatHora(entry.created_at)}</span>
                                                </div>
                                                <p className="text-sm leading-relaxed">{entry.mensaje}</p>
                                                {entry.ubicacion && (
                                                    <div className="flex items-center gap-1 mt-1">
                                                        <MapPin className="h-3 w-3 text-muted-foreground/60" />
                                                        <span className="text-xs text-muted-foreground/60">{entry.ubicacion}</span>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                    <div ref={bottomRef} />
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Add comment form */}
                    <Card>
                        <CardContent className="pt-4 pb-4 px-4">
                            <p className="text-xs font-medium mb-3 text-muted-foreground uppercase tracking-wide">Nueva actualización</p>
                            <div className="space-y-2">
                                <input
                                    type="text"
                                    value={nuevoComentario}
                                    onChange={e => setNuevoComentario(e.target.value)}
                                    onKeyDown={e => e.key === "Enter" && !e.shiftKey && enviarComentario()}
                                    placeholder="Escribe una actualización de tracking..."
                                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                                />
                                <div className="flex gap-2">
                                    <input
                                        type="text"
                                        value={ubicacion}
                                        onChange={e => setUbicacion(e.target.value)}
                                        placeholder="Ubicación (opcional)"
                                        className="flex-1 rounded-md border border-input bg-background px-3 py-2 text-xs focus:outline-none focus:ring-2 focus:ring-ring"
                                    />
                                    <button
                                        onClick={enviarComentario}
                                        disabled={!nuevoComentario.trim()}
                                        className="flex items-center gap-1.5 rounded-md bg-foreground px-3 py-2 text-sm text-background hover:bg-foreground/90 disabled:opacity-40 transition-colors"
                                    >
                                        <Send className="h-3.5 w-3.5" />
                                        {wsStatus === "connected" ? "Enviar" : "Añadir"}
                                    </button>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            )}

            {/* GASTOS TAB */}
            {activeTab === "gastos" && (
                <div className="max-w-2xl">
                    <Card>
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="border-b border-border">
                                        {["Tipo", "Descripción", "Monto"].map(h => (
                                            <th key={h} className="text-left text-xs font-medium text-muted-foreground px-4 py-3 first:pl-5 last:pr-5 last:text-right">{h}</th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-border">
                                    {GASTOS_MOCK.map((g, i) => (
                                        <tr key={i} className="hover:bg-muted/30">
                                            <td className="px-5 py-3">
                                                <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium border ${g.tipo === "Caseta" ? "bg-violet-500/15 text-violet-400 border-violet-500/30" :
                                                    g.tipo === "Combustible" ? "bg-blue-500/15 text-blue-400 border-blue-500/30" :
                                                        "bg-muted text-muted-foreground border-border"
                                                    }`}>{g.tipo}</span>
                                            </td>
                                            <td className="px-4 py-3 text-xs text-muted-foreground">{g.descripcion}</td>
                                            <td className="px-4 pr-5 py-3 text-xs font-medium tabular-nums text-right">{MXN(g.monto)}</td>
                                        </tr>
                                    ))}
                                </tbody>
                                <tfoot>
                                    <tr className="border-t border-border bg-muted/20">
                                        <td colSpan={2} className="px-5 py-3 text-sm font-semibold">Total gastos</td>
                                        <td className="px-4 pr-5 py-3 text-sm font-bold tabular-nums text-right">{MXN(totalGastos)}</td>
                                    </tr>
                                </tfoot>
                            </table>
                        </div>
                    </Card>
                </div>
            )}

            {/* RENTABILIDAD TAB */}
            {activeTab === "rentabilidad" && (
                <div className="max-w-xl space-y-4">
                    <Card>
                        <CardHeader className="px-5 pt-5 pb-3">
                            <CardTitle className="text-sm font-medium flex items-center gap-2">
                                <TrendingUp className="h-4 w-4 text-emerald-400" />
                                Análisis de Rentabilidad
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="px-5 pb-5 space-y-2.5">
                            <div className="flex items-center justify-between py-2.5 border-b border-border">
                                <div>
                                    <div className="text-sm font-medium">Tarifa al cliente</div>
                                    <div className="text-xs text-muted-foreground">{TRIP_MOCK.cliente}</div>
                                </div>
                                <div className="text-base font-bold text-emerald-400 tabular-nums">{MXN(TRIP_MOCK.tarifa_cliente)}</div>
                            </div>
                            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide pt-1">Gastos operativos</p>
                            {GASTOS_MOCK.map((g, i) => (
                                <div key={i} className="flex items-center justify-between text-sm">
                                    <span className="text-muted-foreground">{g.tipo} — {g.descripcion}</span>
                                    <span className="text-destructive tabular-nums">- {MXN(g.monto)}</span>
                                </div>
                            ))}
                            <div className="flex items-center justify-between text-sm border-t border-border pt-2.5">
                                <span className="text-muted-foreground font-medium">Total gastos</span>
                                <span className="text-destructive font-medium tabular-nums">- {MXN(totalGastos)}</span>
                            </div>
                            <div className="rounded-lg bg-muted/40 border border-border p-4 mt-3">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <div className="text-xs text-muted-foreground uppercase tracking-wide font-medium">Utilidad bruta</div>
                                        <div className="text-2xl font-bold text-emerald-400 tabular-nums mt-0.5">{MXN(utilidadBruta)}</div>
                                    </div>
                                    <div className="text-right">
                                        <div className="text-xs text-muted-foreground uppercase tracking-wide font-medium">Margen</div>
                                        <div className="text-2xl font-bold tabular-nums mt-0.5">{margen}%</div>
                                    </div>
                                </div>
                                <div className="mt-3">
                                    <div className="h-2 rounded-full bg-muted overflow-hidden">
                                        <div className="h-full rounded-full bg-emerald-500 transition-all" style={{ width: `${margen}%` }} />
                                    </div>
                                    <div className="flex justify-between text-xs text-muted-foreground mt-1">
                                        <span>Gastos ({(100 - parseFloat(margen)).toFixed(1)}%)</span>
                                        <span>Utilidad ({margen}%)</span>
                                    </div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            )}
        </div>
    )
}
