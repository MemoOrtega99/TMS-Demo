"use client"

import { useState } from "react"
import { Bell, Check, CheckCheck, AlertTriangle, Truck, FileText, Package, Wrench } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

type Priority = "urgente" | "alta" | "media" | "baja"
type NotifType = "factura_vencida" | "factura_por_vencer" | "viaje_en_ruta" | "viaje_completado" | "tracking_update" | "stock_bajo" | "servicio_proximo"

interface Notification {
    id: number
    tipo: NotifType
    titulo: string
    mensaje: string
    prioridad: Priority
    leida: boolean
    created_at: string
    referencia_tipo?: string
}

const MOCK_NOTIFS: Notification[] = [
    { id: 1, tipo: "factura_vencida", titulo: "Factura vencida", mensaje: "FAC-2026-001 de Grupo Bimbo venció hace 15 días — Saldo: $127,500.00", prioridad: "urgente", leida: false, created_at: "2026-03-01T09:00:00Z", referencia_tipo: "invoice" },
    { id: 2, tipo: "factura_vencida", titulo: "Factura vencida", mensaje: "FAC-2026-005 de Liverpool venció hace 12 días — Saldo: $89,500.00", prioridad: "urgente", leida: false, created_at: "2026-03-01T09:05:00Z", referencia_tipo: "invoice" },
    { id: 3, tipo: "factura_por_vencer", titulo: "Factura próxima a vencer", mensaje: "FAC-2026-002 de FEMSA Logística vence en 3 días — Saldo: $72,800.00", prioridad: "alta", leida: false, created_at: "2026-03-01T10:00:00Z", referencia_tipo: "invoice" },
    { id: 4, tipo: "stock_bajo", titulo: "Stock bajo en inventario", mensaje: "Filtro de aceite motor — Quedan 2 pzas (mínimo: 5 pzas)", prioridad: "alta", leida: false, created_at: "2026-03-01T11:00:00Z", referencia_tipo: "inventory" },
    { id: 5, tipo: "viaje_en_ruta", titulo: "Viaje en ruta", mensaje: "VJ-2026-0018 (ECO-003) salió de Altamira hacia Monterrey", prioridad: "media", leida: false, created_at: "2026-03-01T08:30:00Z", referencia_tipo: "trip" },
    { id: 6, tipo: "servicio_proximo", titulo: "Servicio preventivo próximo", mensaje: "ECO-007 (Kenworth W990) — Servicio preventivo programado para esta semana", prioridad: "media", leida: true, created_at: "2026-02-28T14:00:00Z", referencia_tipo: "vehicle" },
    { id: 7, tipo: "tracking_update", titulo: "Actualización de tracking", mensaje: "VJ-2026-0017: Unidad ECO-005 pasó caseta de Tamazunchale, SLP", prioridad: "baja", leida: true, created_at: "2026-03-01T13:45:00Z", referencia_tipo: "trip" },
    { id: 8, tipo: "viaje_completado", titulo: "Viaje completado", mensaje: "VJ-2026-0016 entregó en Laredo, TX — Tarifa: $95,000 MXN", prioridad: "baja", leida: true, created_at: "2026-02-28T18:00:00Z", referencia_tipo: "trip" },
    { id: 9, tipo: "tracking_update", titulo: "Actualización de tracking", mensaje: "VJ-2026-0018: Operador reporta retraso por revisión en caseta Linares — ETA +2h", prioridad: "media", leida: false, created_at: "2026-03-01T15:20:00Z", referencia_tipo: "trip" },
]

const priorityConfig: Record<Priority, { class: string; dot: string; label: string }> = {
    urgente: { class: "bg-red-500/15 text-red-400 border-red-500/30", dot: "bg-red-500", label: "Urgente" },
    alta: { class: "bg-orange-500/15 text-orange-400 border-orange-500/30", dot: "bg-orange-500", label: "Alta" },
    media: { class: "bg-blue-500/15 text-blue-400 border-blue-500/30", dot: "bg-blue-500", label: "Media" },
    baja: { class: "bg-muted text-muted-foreground border-border", dot: "bg-muted-foreground", label: "Baja" },
}

const typeIcon: Record<NotifType, React.ElementType> = {
    factura_vencida: AlertTriangle,
    factura_por_vencer: FileText,
    viaje_en_ruta: Truck,
    viaje_completado: Check,
    tracking_update: Truck,
    stock_bajo: Package,
    servicio_proximo: Wrench,
}

function timeAgo(dateStr: string) {
    const diff = Math.floor((Date.now() - new Date(dateStr).getTime()) / 60000)
    if (diff < 60) return `hace ${diff} min`
    if (diff < 1440) return `hace ${Math.floor(diff / 60)}h`
    return `hace ${Math.floor(diff / 1440)}d`
}

export default function NotificacionesPage() {
    const [notifs, setNotifs] = useState<Notification[]>(MOCK_NOTIFS)
    const [filter, setFilter] = useState<"todas" | "no_leidas">("todas")

    const unreadCount = notifs.filter(n => !n.leida).length

    function markRead(id: number) {
        setNotifs(prev => prev.map(n => n.id === id ? { ...n, leida: true } : n))
    }

    function markAllRead() {
        setNotifs(prev => prev.map(n => ({ ...n, leida: true })))
    }

    const displayed = filter === "no_leidas" ? notifs.filter(n => !n.leida) : notifs

    return (
        <div className="space-y-6 max-w-3xl">
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-xs text-muted-foreground uppercase tracking-widest font-medium">Sistema</p>
                    <h1 className="text-2xl font-semibold tracking-tight mt-0.5 flex items-center gap-2">
                        <Bell className="h-5 w-5" />
                        Notificaciones
                        {unreadCount > 0 && (
                            <span className="ml-1 flex h-5 items-center justify-center rounded-full bg-destructive px-1.5 text-xs font-medium text-white min-w-[20px]">
                                {unreadCount}
                            </span>
                        )}
                    </h1>
                </div>
                {unreadCount > 0 && (
                    <button
                        onClick={markAllRead}
                        className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
                    >
                        <CheckCheck className="h-4 w-4" />
                        Marcar todas como leídas
                    </button>
                )}
            </div>

            {/* Filter tabs */}
            <div className="flex gap-1 rounded-lg border border-border bg-muted/30 p-1 w-fit">
                {(["todas", "no_leidas"] as const).map(f => (
                    <button
                        key={f}
                        onClick={() => setFilter(f)}
                        className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${filter === f ? "bg-background shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground"}`}
                    >
                        {f === "todas" ? "Todas" : `Sin leer (${unreadCount})`}
                    </button>
                ))}
            </div>

            {/* Notifications list */}
            <div className="space-y-2">
                {displayed.map(n => {
                    const Icon = typeIcon[n.tipo]
                    const p = priorityConfig[n.prioridad]
                    return (
                        <Card
                            key={n.id}
                            className={`transition-all cursor-pointer hover:shadow-sm ${n.leida ? "opacity-60" : "border-l-2 border-l-foreground/20"}`}
                            onClick={() => markRead(n.id)}
                        >
                            <CardContent className="pt-3 pb-3 px-4">
                                <div className="flex items-start gap-3">
                                    <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full border ${p.class} mt-0.5`}>
                                        <Icon className="h-3.5 w-3.5" />
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center justify-between gap-2">
                                            <p className={`text-sm font-medium ${n.leida ? "text-muted-foreground" : "text-foreground"}`}>
                                                {n.titulo}
                                            </p>
                                            <div className="flex items-center gap-2 shrink-0">
                                                <span className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full text-xs border ${p.class}`}>
                                                    <span className={`h-1.5 w-1.5 rounded-full ${p.dot}`} />
                                                    {p.label}
                                                </span>
                                                {!n.leida && (
                                                    <span className="h-2 w-2 rounded-full bg-foreground" />
                                                )}
                                            </div>
                                        </div>
                                        <p className="text-xs text-muted-foreground mt-0.5 leading-relaxed">{n.mensaje}</p>
                                        <p className="text-xs text-muted-foreground/60 mt-1.5">{timeAgo(n.created_at)}</p>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    )
                })}

                {displayed.length === 0 && (
                    <Card>
                        <CardContent className="py-12 text-center">
                            <Bell className="h-8 w-8 text-muted-foreground/30 mx-auto mb-3" />
                            <p className="text-sm text-muted-foreground">Sin notificaciones sin leer</p>
                        </CardContent>
                    </Card>
                )}
            </div>
        </div>
    )
}
