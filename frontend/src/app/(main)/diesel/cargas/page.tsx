"use client"

import { useState } from "react"
import { Search, Fuel } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"

interface DieselLoad {
    id: number
    unidad: string
    operador: string
    tipo: "PATIO" | "GASOLINERA"
    litros: number
    costo_por_litro: number
    costo_total: number
    km_odometro: number
    fecha_carga: string
    viaje?: string
}

const MOCK_DIESEL: DieselLoad[] = [
    { id: 1, unidad: "ECO-003", operador: "J. Martínez Soto", tipo: "GASOLINERA", litros: 280, costo_por_litro: 25.50, costo_total: 7140, km_odometro: 98200, fecha_carga: "2026-03-01", viaje: "VJ-2026-0018" },
    { id: 2, unidad: "ECO-005", operador: "R. González López", tipo: "GASOLINERA", litros: 320, costo_por_litro: 25.80, costo_total: 8256, km_odometro: 187700, fecha_carga: "2026-03-01", viaje: "VJ-2026-0017" },
    { id: 3, unidad: "ECO-001", operador: "A. López García", tipo: "PATIO", litros: 400, costo_por_litro: 24.50, costo_total: 9800, km_odometro: 145100, fecha_carga: "2026-02-28" },
    { id: 4, unidad: "ECO-002", operador: "E. Ramírez Cruz", tipo: "PATIO", litros: 350, costo_por_litro: 24.50, costo_total: 8575, km_odometro: 210400, fecha_carga: "2026-02-27" },
    { id: 5, unidad: "ECO-004", operador: "H. Vega Torres", tipo: "GASOLINERA", litros: 260, costo_por_litro: 25.20, costo_total: 6552, km_odometro: 320700, fecha_carga: "2026-02-25", viaje: "VJ-2026-0013" },
    { id: 6, unidad: "ECO-006", operador: "C. Morales Ruiz", tipo: "GASOLINERA", litros: 300, costo_por_litro: 25.40, costo_total: 7620, km_odometro: 256800, fecha_carga: "2026-02-24", viaje: "VJ-2026-0012" },
    { id: 7, unidad: "ECO-003", operador: "J. Martínez Soto", tipo: "PATIO", litros: 500, costo_por_litro: 24.50, costo_total: 12250, km_odometro: 97900, fecha_carga: "2026-02-20" },
]

const MXN = (v: number) => new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN", maximumFractionDigits: 0 }).format(v)
const NUM = (v: number) => new Intl.NumberFormat("es-MX").format(v)

export default function DieselCargasPage() {
    const [search, setSearch] = useState("")
    const filtered = MOCK_DIESEL.filter(d =>
        !search || [d.unidad, d.operador, d.viaje ?? ""].some(f => f.toLowerCase().includes(search.toLowerCase()))
    )

    const totalLitros = MOCK_DIESEL.reduce((a, d) => a + d.litros, 0)
    const totalCosto = MOCK_DIESEL.reduce((a, d) => a + d.costo_total, 0)
    const promPorLitro = totalCosto / totalLitros

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-xs text-muted-foreground uppercase tracking-widest font-medium">Diesel</p>
                    <h1 className="text-2xl font-semibold tracking-tight mt-0.5">Cargas de Diesel</h1>
                </div>
            </div>

            <div className="grid grid-cols-3 gap-3">
                <Card><CardContent className="pt-4 pb-4 px-4">
                    <div className="text-xl font-bold">{NUM(totalLitros)} L</div>
                    <div className="text-xs text-muted-foreground mt-1">Total litros cargados</div>
                </CardContent></Card>
                <Card><CardContent className="pt-4 pb-4 px-4">
                    <div className="text-xl font-bold tabular-nums">{MXN(totalCosto)}</div>
                    <div className="text-xs text-muted-foreground mt-1">Costo total combustible</div>
                </CardContent></Card>
                <Card><CardContent className="pt-4 pb-4 px-4">
                    <div className="text-xl font-bold tabular-nums">${promPorLitro.toFixed(2)}/L</div>
                    <div className="text-xs text-muted-foreground mt-1">Precio promedio</div>
                </CardContent></Card>
            </div>

            <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <input type="text" placeholder="Buscar por unidad, operador, viaje..." value={search} onChange={e => setSearch(e.target.value)}
                    className="w-full pl-9 pr-3 py-2 text-sm border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring" />
            </div>

            <Card>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-border">
                                {["Fecha", "Unidad", "Operador", "Tipo", "Litros", "$/L", "Total", "Odómetro", "Viaje"].map(h => (
                                    <th key={h} className="text-left text-xs font-medium text-muted-foreground px-4 py-3 first:pl-5 last:pr-5 whitespace-nowrap">{h}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-border">
                            {filtered.map(d => (
                                <tr key={d.id} className="hover:bg-muted/30 transition-colors">
                                    <td className="px-5 py-3.5 text-xs text-muted-foreground">{d.fecha_carga}</td>
                                    <td className="px-4 py-3.5 font-mono text-xs font-semibold">{d.unidad}</td>
                                    <td className="px-4 py-3.5 text-xs text-muted-foreground">{d.operador}</td>
                                    <td className="px-4 py-3.5">
                                        <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium border ${d.tipo === "PATIO" ? "bg-blue-500/15 text-blue-400 border-blue-500/30" : "bg-orange-500/15 text-orange-400 border-orange-500/30"}`}>
                                            <Fuel className="h-2.5 w-2.5" />
                                            {d.tipo.charAt(0) + d.tipo.slice(1).toLowerCase()}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3.5 text-xs font-medium tabular-nums">{NUM(d.litros)} L</td>
                                    <td className="px-4 py-3.5 text-xs text-muted-foreground tabular-nums">${d.costo_por_litro.toFixed(2)}</td>
                                    <td className="px-4 py-3.5 text-xs font-medium tabular-nums">{MXN(d.costo_total)}</td>
                                    <td className="px-4 py-3.5 text-xs text-muted-foreground tabular-nums">{NUM(d.km_odometro)} km</td>
                                    <td className="px-4 pr-5 py-3.5 font-mono text-xs text-muted-foreground">{d.viaje ?? "—"}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </Card>
        </div>
    )
}
