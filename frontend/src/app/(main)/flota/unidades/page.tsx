"use client"

import { useState, useEffect } from "react"
import { Truck, Plus, Search, Wrench, CheckCircle, AlertCircle } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"

type VehicleStatus = "DISPONIBLE" | "EN_RUTA" | "TALLER" | "BAJA"

interface Vehicle {
    id: number
    numero_economico: string
    marca: string
    modelo: string
    anio: number
    placas: string
    tipo_vehiculo: string
    estatus: VehicleStatus
    km_actual: number
    chofer?: string
}

const MOCK_VEHICLES: Vehicle[] = [
    { id: 1, numero_economico: "ECO-001", marca: "Kenworth", modelo: "T680", anio: 2022, placas: "SBD-123-A", tipo_vehiculo: "TRACTO", estatus: "DISPONIBLE", km_actual: 145200, chofer: "A. López García" },
    { id: 2, numero_economico: "ECO-002", marca: "Freightliner", modelo: "Cascadia", anio: 2021, placas: "SBD-456-B", tipo_vehiculo: "TRACTO", estatus: "DISPONIBLE", km_actual: 210500 },
    { id: 3, numero_economico: "ECO-003", marca: "Kenworth", modelo: "T680", anio: 2023, placas: "SBD-789-C", tipo_vehiculo: "TRACTO", estatus: "EN_RUTA", km_actual: 98300, chofer: "J. Martínez Soto" },
    { id: 4, numero_economico: "ECO-004", marca: "International", modelo: "LT", anio: 2020, placas: "SBD-012-D", tipo_vehiculo: "TRACTO", estatus: "EN_RUTA", km_actual: 320800, chofer: "H. Vega Torres" },
    { id: 5, numero_economico: "ECO-005", marca: "Peterbilt", modelo: "389", anio: 2022, placas: "SBD-345-E", tipo_vehiculo: "TRACTO", estatus: "EN_RUTA", km_actual: 187600, chofer: "R. González López" },
    { id: 6, numero_economico: "ECO-006", marca: "Freightliner", modelo: "Cascadia", anio: 2021, placas: "SBD-678-F", tipo_vehiculo: "TRACTO", estatus: "EN_RUTA", km_actual: 256900, chofer: "C. Morales Ruiz" },
    { id: 7, numero_economico: "ECO-007", marca: "Kenworth", modelo: "W990", anio: 2019, placas: "SBD-901-G", tipo_vehiculo: "TRACTO", estatus: "TALLER", km_actual: 415200 },
    { id: 8, numero_economico: "ECO-008", marca: "International", modelo: "LT", anio: 2023, placas: "SBD-234-H", tipo_vehiculo: "TRACTO", estatus: "EN_RUTA", km_actual: 52100, chofer: "L. Castro Díaz" },
]

const statusConfig: Record<VehicleStatus, { label: string; class: string; dot: string }> = {
    DISPONIBLE: { label: "Disponible", class: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30", dot: "bg-emerald-500" },
    EN_RUTA: { label: "En Ruta", class: "bg-blue-500/15 text-blue-400 border-blue-500/30", dot: "bg-blue-500" },
    TALLER: { label: "En Taller", class: "bg-yellow-500/15 text-yellow-400 border-yellow-500/30", dot: "bg-yellow-500" },
    BAJA: { label: "Baja", class: "bg-muted text-muted-foreground border-border", dot: "bg-muted-foreground" },
}

export default function UnidadesPage() {
    const [vehicles, setVehicles] = useState<Vehicle[]>(MOCK_VEHICLES)
    const [search, setSearch] = useState("")
    const [view, setView] = useState<"grid" | "table">("grid")

    useEffect(() => {
        fetch("http://localhost:8001/api/v1/vehicles", {
            headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
        }).then(r => r.json()).then(data => {
            if (Array.isArray(data?.items)) setVehicles(data.items)
        }).catch(() => { })
    }, [])

    const filtered = vehicles.filter(v =>
        !search || [v.numero_economico, v.marca, v.modelo, v.placas, v.chofer ?? ""]
            .some(f => f.toLowerCase().includes(search.toLowerCase()))
    )

    const counts = {
        total: vehicles.length,
        disponible: vehicles.filter(v => v.estatus === "DISPONIBLE").length,
        en_ruta: vehicles.filter(v => v.estatus === "EN_RUTA").length,
        taller: vehicles.filter(v => v.estatus === "TALLER").length,
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-xs text-muted-foreground uppercase tracking-widest font-medium">Flota</p>
                    <h1 className="text-2xl font-semibold tracking-tight mt-0.5">Unidades</h1>
                </div>
                <button className="flex items-center gap-2 rounded-md bg-foreground px-3.5 py-2 text-sm font-medium text-background hover:bg-foreground/90 transition-colors">
                    <Plus className="h-4 w-4" />
                    Nueva unidad
                </button>
            </div>

            {/* Stats row */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {[
                    { label: "Total flota", value: counts.total, icon: Truck, color: "" },
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

            {/* Search + view toggle */}
            <div className="flex gap-3">
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <input
                        type="text"
                        placeholder="Buscar por ECO, marca, modelo, placas, operador..."
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                        className="w-full pl-9 pr-3 py-2 text-sm border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring"
                    />
                </div>
                <div className="flex rounded-md border border-input overflow-hidden text-xs">
                    {(["grid", "table"] as const).map(v => (
                        <button key={v} onClick={() => setView(v)} className={`px-4 py-2 capitalize transition-colors ${view === v ? "bg-foreground text-background font-medium" : "text-muted-foreground hover:text-foreground"}`}>
                            {v === "grid" ? "Tarjetas" : "Tabla"}
                        </button>
                    ))}
                </div>
            </div>

            {/* Grid view */}
            {view === "grid" && (
                <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                    {filtered.map(v => (
                        <Card key={v.id} className="hover:shadow-md transition-all group cursor-pointer">
                            <CardContent className="pt-4 pb-4 px-4">
                                <div className="flex items-center justify-between mb-3">
                                    <div className="flex items-center gap-2">
                                        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-muted">
                                            <Truck className="h-4 w-4 text-muted-foreground" />
                                        </div>
                                        <div>
                                            <div className="font-mono text-sm font-semibold">{v.numero_economico}</div>
                                            <div className="text-xs text-muted-foreground">{v.placas}</div>
                                        </div>
                                    </div>
                                    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium border ${statusConfig[v.estatus].class}`}>
                                        <span className={`h-1.5 w-1.5 rounded-full ${statusConfig[v.estatus].dot}`} />
                                        {statusConfig[v.estatus].label}
                                    </span>
                                </div>
                                <div className="space-y-1.5">
                                    <div className="text-sm font-medium">{v.marca} {v.modelo} {v.anio}</div>
                                    <div className="text-xs text-muted-foreground">{(v.km_actual).toLocaleString("es-MX")} km</div>
                                    {v.chofer && <div className="text-xs text-muted-foreground">Op: {v.chofer}</div>}
                                    {v.estatus === "TALLER" && (
                                        <div className="flex items-center gap-1.5 text-xs text-yellow-400 mt-2 pt-2 border-t border-border">
                                            <AlertCircle className="h-3 w-3" />
                                            Requiere atención
                                        </div>
                                    )}
                                </div>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            )}

            {/* Table view */}
            {view === "table" && (
                <Card>
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="border-b border-border">
                                    {["ECO", "Marca / Modelo", "Año", "Placas", "Odómetro", "Operador asignado", "Estatus"].map(h => (
                                        <th key={h} className="text-left text-xs font-medium text-muted-foreground px-4 py-3 first:pl-5 last:pr-5 whitespace-nowrap">{h}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-border">
                                {filtered.map(v => (
                                    <tr key={v.id} className="hover:bg-muted/30 transition-colors cursor-pointer">
                                        <td className="px-5 py-3.5 font-mono text-xs font-semibold">{v.numero_economico}</td>
                                        <td className="px-4 py-3.5 text-xs">{v.marca} {v.modelo}</td>
                                        <td className="px-4 py-3.5 text-xs text-muted-foreground">{v.anio}</td>
                                        <td className="px-4 py-3.5 font-mono text-xs">{v.placas}</td>
                                        <td className="px-4 py-3.5 text-xs tabular-nums text-muted-foreground">{v.km_actual.toLocaleString("es-MX")} km</td>
                                        <td className="px-4 py-3.5 text-xs text-muted-foreground">{v.chofer ?? "—"}</td>
                                        <td className="px-4 pr-5 py-3.5">
                                            <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium border ${statusConfig[v.estatus].class}`}>
                                                <span className={`h-1.5 w-1.5 rounded-full ${statusConfig[v.estatus].dot}`} />
                                                {statusConfig[v.estatus].label}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </Card>
            )}
        </div>
    )
}
