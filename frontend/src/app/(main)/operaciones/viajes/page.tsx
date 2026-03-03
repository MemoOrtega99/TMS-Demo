"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { ArrowRight, Calendar, MapPin, Plus, Search, Filter } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

type TripStatus = "programado" | "asignado" | "en_ruta" | "completado" | "cancelado"

interface Trip {
    numero: string
    origen: string
    destino: string
    estatus: TripStatus
    unidad: string
    operador: string
    cliente: string
    fecha_programada: string
    tarifa_cliente: number
}

const MOCK_TRIPS: Trip[] = [
    { numero: "VJ-2026-0018", origen: "Altamira, Tam", destino: "Monterrey, NL", estatus: "en_ruta", unidad: "ECO-003", operador: "J. Martínez Soto", cliente: "Grupo Bimbo", fecha_programada: "2026-03-01", tarifa_cliente: 85000 },
    { numero: "VJ-2026-0017", origen: "Tampico, Tam", destino: "Ciudad de México", estatus: "en_ruta", unidad: "ECO-005", operador: "R. González López", cliente: "FEMSA Logística", fecha_programada: "2026-03-01", tarifa_cliente: 120000 },
    { numero: "VJ-2026-0016", origen: "Monterrey, NL", destino: "Laredo, TX", estatus: "completado", unidad: "ECO-001", operador: "A. López García", cliente: "Ternium", fecha_programada: "2026-02-28", tarifa_cliente: 95000 },
    { numero: "VJ-2026-0015", origen: "Altamira, Tam", destino: "Guadalajara, Jal", estatus: "programado", unidad: "ECO-007", operador: "M. Flores Hdez", cliente: "Liverpool", fecha_programada: "2026-03-03", tarifa_cliente: 110000 },
    { numero: "VJ-2026-0014", origen: "Saltillo, Coah", destino: "Monterrey, NL", estatus: "completado", unidad: "ECO-002", operador: "E. Ramírez Cruz", cliente: "Cemex", fecha_programada: "2026-02-27", tarifa_cliente: 65000 },
    { numero: "VJ-2026-0013", origen: "Altamira, Tam", destino: "CDMX", estatus: "completado", unidad: "ECO-004", operador: "H. Vega Torres", cliente: "Whirlpool", fecha_programada: "2026-02-25", tarifa_cliente: 115000 },
    { numero: "VJ-2026-0012", origen: "Monterrey, NL", destino: "Saltillo, Coah", estatus: "completado", unidad: "ECO-006", operador: "C. Morales Ruiz", cliente: "ArcelorMittal", fecha_programada: "2026-02-24", tarifa_cliente: 55000 },
    { numero: "VJ-2026-0011", origen: "Tampico, Tam", destino: "Monterrey, NL", estatus: "cancelado", unidad: "ECO-008", operador: "L. Castro Díaz", cliente: "Peñoles", fecha_programada: "2026-02-22", tarifa_cliente: 75000 },
]

const statusConfig: Record<TripStatus, { label: string; class: string }> = {
    en_ruta: { label: "En Ruta", class: "bg-blue-500/15 text-blue-400 border-blue-500/30" },
    completado: { label: "Completado", class: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30" },
    programado: { label: "Programado", class: "bg-yellow-500/15 text-yellow-400 border-yellow-500/30" },
    asignado: { label: "Asignado", class: "bg-violet-500/15 text-violet-400 border-violet-500/30" },
    cancelado: { label: "Cancelado", class: "bg-red-500/15 text-red-400 border-red-500/30" },
}

const MXN = (v: number) => new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN", maximumFractionDigits: 0 }).format(v)

export default function ViajesPage() {
    const [trips, setTrips] = useState<Trip[]>(MOCK_TRIPS)
    const [filter, setFilter] = useState<TripStatus | "todos">("todos")
    const [search, setSearch] = useState("")

    useEffect(() => {
        fetch("http://localhost:8001/api/v1/trips", {
            headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
        }).then(r => r.json()).then(data => {
            if (Array.isArray(data?.items)) setTrips(data.items)
        }).catch(() => {/* use mock */ })
    }, [])

    const filtered = trips.filter(t => {
        const matchStatus = filter === "todos" || t.estatus === filter
        const matchSearch = !search || [t.numero, t.origen, t.destino, t.cliente, t.unidad, t.operador]
            .some(f => f.toLowerCase().includes(search.toLowerCase()))
        return matchStatus && matchSearch
    })

    const counts = {
        en_ruta: trips.filter(t => t.estatus === "en_ruta").length,
        programado: trips.filter(t => t.estatus === "programado").length,
        completado: trips.filter(t => t.estatus === "completado").length,
        total: trips.length,
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-xs text-muted-foreground uppercase tracking-widest font-medium">Operaciones</p>
                    <h1 className="text-2xl font-semibold tracking-tight mt-0.5">Viajes</h1>
                </div>
                <Link href="/operaciones/viajes/nuevo" className="flex items-center gap-2 rounded-md bg-foreground px-3.5 py-2 text-sm font-medium text-background hover:bg-foreground/90 transition-colors cursor-pointer">
                    <Plus className="h-4 w-4" />
                    Nuevo viaje
                </Link>
            </div>

            {/* Summary cards */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {[
                    { label: "Total viajes", value: counts.total, color: "" },
                    { label: "En ruta", value: counts.en_ruta, color: "text-blue-400" },
                    { label: "Programados", value: counts.programado, color: "text-yellow-400" },
                    { label: "Completados", value: counts.completado, color: "text-emerald-400" },
                ].map(s => (
                    <Card key={s.label}>
                        <CardContent className="pt-4 pb-4 px-4">
                            <div className={`text-2xl font-bold ${s.color}`}>{s.value}</div>
                            <div className="text-xs text-muted-foreground mt-1">{s.label}</div>
                        </CardContent>
                    </Card>
                ))}
            </div>

            {/* Filters */}
            <Card>
                <CardContent className="pt-4 pb-4 px-4">
                    <div className="flex flex-col sm:flex-row gap-3">
                        <div className="relative flex-1">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                            <input
                                type="text"
                                placeholder="Buscar por número, ruta, cliente, unidad..."
                                value={search}
                                onChange={e => setSearch(e.target.value)}
                                className="w-full pl-9 pr-3 py-2 text-sm border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring"
                            />
                        </div>
                        <div className="flex items-center gap-2">
                            <Filter className="h-4 w-4 text-muted-foreground" />
                            <div className="flex rounded-md border border-input overflow-hidden text-xs">
                                {(["todos", "en_ruta", "programado", "completado", "cancelado"] as const).map(s => (
                                    <button
                                        key={s}
                                        onClick={() => setFilter(s)}
                                        className={`px-3 py-2 capitalize transition-colors ${filter === s ? "bg-foreground text-background font-medium" : "text-muted-foreground hover:text-foreground hover:bg-muted/50"}`}
                                    >
                                        {s === "todos" ? "Todos" : statusConfig[s as TripStatus]?.label ?? s}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Trips Table */}
            <Card>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-border">
                                {["# Viaje", "Ruta", "Cliente", "Unidad / Op.", "Fecha", "Tarifa", "Estatus", ""].map(h => (
                                    <th key={h} className="text-left text-xs font-medium text-muted-foreground px-4 py-3 first:pl-5 last:pr-5">{h}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-border">
                            {filtered.map((trip: any, i: number) => (
                                <tr key={trip.numero || trip.numero_viaje || trip.id || i} className="hover:bg-muted/30 transition-colors group">
                                    <td className="px-5 py-3.5 font-mono text-xs font-medium">{trip.numero || trip.numero_viaje}</td>
                                    <td className="px-4 py-3.5">
                                        <div className="flex items-center gap-1.5 text-xs">
                                            <MapPin className="h-3 w-3 text-muted-foreground shrink-0" />
                                            <span className="text-muted-foreground">{trip.origen}</span>
                                            <ArrowRight className="h-3 w-3 text-muted-foreground shrink-0" />
                                            <span>{trip.destino}</span>
                                        </div>
                                    </td>
                                    <td className="px-4 py-3.5 text-xs text-muted-foreground">{trip.cliente}</td>
                                    <td className="px-4 py-3.5">
                                        <div className="text-xs font-medium">{trip.unidad}</div>
                                        <div className="text-xs text-muted-foreground">{trip.operador}</div>
                                    </td>
                                    <td className="px-4 py-3.5">
                                        <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                                            <Calendar className="h-3 w-3" />
                                            {trip.fecha_programada}
                                        </div>
                                    </td>
                                    <td className="px-4 py-3.5 text-xs font-medium tabular-nums">{MXN(trip.tarifa_cliente)}</td>
                                    <td className="px-4 py-3.5">
                                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border ${statusConfig[trip.estatus].class}`}>
                                            {statusConfig[trip.estatus].label}
                                        </span>
                                    </td>
                                    <td className="px-5 py-3.5">
                                        <Link href={`/operaciones/viajes/${trip.numero}`} className="text-xs text-muted-foreground hover:text-foreground opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                                            Ver →
                                        </Link>
                                    </td>
                                </tr>
                            ))}
                            {filtered.length === 0 && (
                                <tr>
                                    <td colSpan={8} className="px-5 py-10 text-center text-sm text-muted-foreground">
                                        No se encontraron viajes
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </Card>
        </div>
    )
}
