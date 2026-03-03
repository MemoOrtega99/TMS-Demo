"use client"

import { useState, useEffect } from "react"
import { Truck, Plus, Search, Wrench, CheckCircle, Box } from "lucide-react"
import Link from "next/link"
import { Card, CardContent } from "@/components/ui/card"

type UnitStatus = "DISPONIBLE" | "EN_RUTA" | "TALLER" | "BAJA"

interface Trailer {
    id: number
    numero_economico: string
    tipo: string
    marca: string
    modelo: string
    anio: number
    placas: string
    capacidad_carga_ton: number
    estatus: UnitStatus
}

const statusConfig: Record<UnitStatus, { label: string; class: string; dot: string }> = {
    DISPONIBLE: { label: "Disponible", class: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30", dot: "bg-emerald-500" },
    EN_RUTA: { label: "En Ruta", class: "bg-blue-500/15 text-blue-400 border-blue-500/30", dot: "bg-blue-500" },
    TALLER: { label: "En Taller", class: "bg-yellow-500/15 text-yellow-400 border-yellow-500/30", dot: "bg-yellow-500" },
    BAJA: { label: "Baja", class: "bg-muted text-muted-foreground border-border", dot: "bg-muted-foreground" },
}

export default function RemolquesPage() {
    const [trailers, setTrailers] = useState<Trailer[]>([])
    const [search, setSearch] = useState("")

    useEffect(() => {
        fetch("http://localhost:8001/api/v1/trailers", {
            headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
        }).then(r => r.json()).then(data => {
            if (Array.isArray(data?.items)) setTrailers(data.items)
        }).catch(() => { })
    }, [])

    const filtered = trailers.filter(t =>
        !search || [t.numero_economico, t.marca, t.modelo, t.placas, t.tipo]
            .some(f => (f || "").toLowerCase().includes(search.toLowerCase()))
    )

    const counts = {
        total: trailers.length,
        disponible: trailers.filter(t => t.estatus === "DISPONIBLE").length,
        en_ruta: trailers.filter(t => t.estatus === "EN_RUTA").length,
        taller: trailers.filter(t => t.estatus === "TALLER").length,
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-xs text-muted-foreground uppercase tracking-widest font-medium">Flota</p>
                    <h1 className="text-2xl font-semibold tracking-tight mt-0.5">Remolques</h1>
                </div>
                <Link href="/flota/remolques/nuevo" className="flex items-center gap-2 rounded-md bg-foreground px-3.5 py-2 text-sm font-medium text-background hover:bg-foreground/90 transition-colors cursor-pointer">
                    <Plus className="h-4 w-4" />
                    Nuevo remolque
                </Link>
            </div>

            {/* Stats row */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {[
                    { label: "Total remolques", value: counts.total, icon: Box, color: "" },
                    { label: "En ruta", value: counts.en_ruta, icon: Truck, color: "text-blue-400" },
                    { label: "Disponibles", value: counts.disponible, icon: CheckCircle, color: "text-emerald-400" },
                    { label: "En taller", value: counts.taller, icon: Wrench, color: "text-yellow-400" },
                ].map(s => (
                    <Card key={s.label}>
                        <CardContent className="pt-4 pb-4 px-4 flex items-center justify-between">
                            <div>
                                <div className={`text-2xl font-bold ${s.color}`}>{s.value}</div>
                                <div className="text-xs text-muted-foreground mt-1">{s.label}</div>
                            </div>
                            <s.icon className={`h-5 w-5 ${s.color || "text-muted-foreground/40"}`} />
                        </CardContent>
                    </Card>
                ))}
            </div>

            {/* Search */}
            <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <input
                    type="text"
                    placeholder="Buscar por ECO, marca, placas o tipo..."
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                    className="w-full pl-9 pr-3 py-2 text-sm border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring"
                />
            </div>

            <Card>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-border">
                                {["ECO", "Tipo", "Marca / Modelo", "Año", "Placas", "Capacidad (Ton)", "Estatus"].map(h => (
                                    <th key={h} className="text-left text-xs font-medium text-muted-foreground px-4 py-3 first:pl-5 last:pr-5 whitespace-nowrap">{h}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-border">
                            {filtered.length === 0 ? (
                                <tr>
                                    <td colSpan={7} className="px-5 py-8 text-center text-sm text-muted-foreground">
                                        No hay remolques registrados.
                                    </td>
                                </tr>
                            ) : filtered.map(t => (
                                <tr key={t.id} className="hover:bg-muted/30 transition-colors">
                                    <td className="px-5 py-3.5 font-mono text-xs font-semibold">{t.numero_economico}</td>
                                    <td className="px-4 py-3.5 text-xs font-medium">{t.tipo.replace("_", " ")}</td>
                                    <td className="px-4 py-3.5 text-xs">{t.marca || "N/A"} {t.modelo || ""}</td>
                                    <td className="px-4 py-3.5 text-xs text-muted-foreground">{t.anio || "—"}</td>
                                    <td className="px-4 py-3.5 font-mono text-xs">{t.placas || "—"}</td>
                                    <td className="px-4 py-3.5 text-xs tabular-nums text-muted-foreground">{t.capacidad_carga_ton ? `${t.capacidad_carga_ton} Ton` : "—"}</td>
                                    <td className="px-4 pr-5 py-3.5">
                                        <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium border ${statusConfig[t.estatus]?.class || "bg-muted text-muted-foreground"}`}>
                                            <span className={`h-1.5 w-1.5 rounded-full ${statusConfig[t.estatus]?.dot || "bg-muted-foreground"}`} />
                                            {statusConfig[t.estatus]?.label || t.estatus}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </Card>
        </div>
    )
}
