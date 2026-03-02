"use client"

import { useState } from "react"
import { Search, Plus, UserCircle, Calendar, CheckCircle, AlertTriangle } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"

interface Driver {
    id: number
    nombre: string
    apellido: string
    licencia_numero: string
    licencia_tipo: string
    licencia_vigencia: string
    telefono: string
    salario_base: number
    estatus: "ACTIVO" | "INACTIVO" | "VACACIONES"
    viajes_mes: number
    unidad_asignada?: string
}

const MOCK_DRIVERS: Driver[] = [
    { id: 1, nombre: "Juan", apellido: "Martínez Soto", licencia_numero: "TAM-2019-001234", licencia_tipo: "E", licencia_vigencia: "2027-05-15", telefono: "831-123-4567", salario_base: 4500, estatus: "ACTIVO", viajes_mes: 4, unidad_asignada: "ECO-003" },
    { id: 2, nombre: "Roberto", apellido: "González López", licencia_numero: "NLE-2020-005678", licencia_tipo: "E", licencia_vigencia: "2026-11-30", telefono: "818-234-5678", salario_base: 5000, estatus: "ACTIVO", viajes_mes: 3, unidad_asignada: "ECO-005" },
    { id: 3, nombre: "Alejandro", apellido: "López García", licencia_numero: "TAM-2018-009012", licencia_tipo: "A", licencia_vigencia: "2025-03-20", telefono: "833-345-6789", salario_base: 4800, estatus: "ACTIVO", viajes_mes: 5, unidad_asignada: "ECO-001" },
    { id: 4, nombre: "Héctor", apellido: "Vega Torres", licencia_numero: "TAM-2021-003456", licencia_tipo: "E", licencia_vigencia: "2028-07-10", telefono: "833-456-7890", salario_base: 4200, estatus: "ACTIVO", viajes_mes: 3, unidad_asignada: "ECO-004" },
    { id: 5, nombre: "Carlos", apellido: "Morales Ruiz", licencia_numero: "NLE-2019-007890", licencia_tipo: "E", licencia_vigencia: "2027-02-28", telefono: "818-567-8901", salario_base: 4600, estatus: "ACTIVO", viajes_mes: 4, unidad_asignada: "ECO-006" },
    { id: 6, nombre: "Marco", apellido: "Flores Hernández", licencia_numero: "TAM-2022-001122", licencia_tipo: "E", licencia_vigencia: "2026-09-15", telefono: "833-678-9012", salario_base: 4300, estatus: "ACTIVO", viajes_mes: 2, unidad_asignada: "ECO-007" },
    { id: 7, nombre: "Luis", apellido: "Castro Díaz", licencia_numero: "TAM-2021-003344", licencia_tipo: "A", licencia_vigencia: "2026-06-01", telefono: "833-789-0123", salario_base: 4100, estatus: "ACTIVO", viajes_mes: 2, unidad_asignada: "ECO-008" },
    { id: 8, nombre: "Ernesto", apellido: "Ramírez Cruz", licencia_numero: "NLE-2020-005566", licencia_tipo: "E", licencia_vigencia: "2027-12-20", telefono: "818-890-1234", salario_base: 4700, estatus: "ACTIVO", viajes_mes: 5, unidad_asignada: "ECO-002" },
    { id: 9, nombre: "Gerardo", apellido: "Peña Villanueva", licencia_numero: "TAM-2017-007788", licencia_tipo: "E", licencia_vigencia: "2025-04-10", telefono: "833-901-2345", salario_base: 4400, estatus: "VACACIONES", viajes_mes: 0 },
    { id: 10, nombre: "Arturo", apellido: "Sánchez Medina", licencia_numero: "NLE-2016-009900", licencia_tipo: "A", licencia_vigencia: "2024-08-31", telefono: "818-012-3456", salario_base: 4000, estatus: "INACTIVO", viajes_mes: 0 },
]

const statusBadge: Record<Driver["estatus"], string> = {
    ACTIVO: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    INACTIVO: "bg-muted text-muted-foreground border-border",
    VACACIONES: "bg-blue-500/15 text-blue-400 border-blue-500/30",
}

const MXN = (v: number) => new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN", maximumFractionDigits: 0 }).format(v)

function isLicenseExpired(dateStr: string) {
    return new Date(dateStr) < new Date()
}
function isLicenseSoon(dateStr: string) {
    const diff = (new Date(dateStr).getTime() - Date.now()) / 86400000
    return diff < 90 && diff >= 0
}

export default function OperadoresPage() {
    const [search, setSearch] = useState("")
    const filtered = MOCK_DRIVERS.filter(d =>
        !search || [d.nombre, d.apellido, d.licencia_numero, d.unidad_asignada ?? ""].some(f => f.toLowerCase().includes(search.toLowerCase()))
    )
    const activos = MOCK_DRIVERS.filter(d => d.estatus === "ACTIVO").length
    const promViajes = (MOCK_DRIVERS.filter(d => d.viajes_mes > 0).reduce((a, d) => a + d.viajes_mes, 0) / MOCK_DRIVERS.filter(d => d.viajes_mes > 0).length).toFixed(1)

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-xs text-muted-foreground uppercase tracking-widest font-medium">Catálogos</p>
                    <h1 className="text-2xl font-semibold tracking-tight mt-0.5">Operadores</h1>
                </div>
                <button className="flex items-center gap-2 rounded-md bg-foreground px-3.5 py-2 text-sm font-medium text-background hover:bg-foreground/90 transition-colors">
                    <Plus className="h-4 w-4" />
                    Nuevo operador
                </button>
            </div>

            <div className="grid grid-cols-3 gap-3">
                <Card><CardContent className="pt-4 pb-4 px-4">
                    <div className="text-xl font-bold">{activos}</div>
                    <div className="text-xs text-muted-foreground mt-1">Activos</div>
                </CardContent></Card>
                <Card><CardContent className="pt-4 pb-4 px-4">
                    <div className="text-xl font-bold">{promViajes}</div>
                    <div className="text-xs text-muted-foreground mt-1">Viajes prom./mes</div>
                </CardContent></Card>
                <Card><CardContent className="pt-4 pb-4 px-4">
                    <div className="text-xl font-bold">{MOCK_DRIVERS.length}</div>
                    <div className="text-xs text-muted-foreground mt-1">Total registrados</div>
                </CardContent></Card>
            </div>

            <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <input type="text" placeholder="Buscar por nombre, licencia, unidad asignada..." value={search} onChange={e => setSearch(e.target.value)}
                    className="w-full pl-9 pr-3 py-2 text-sm border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring" />
            </div>

            <Card>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-border">
                                {["Operador", "Licencia", "Vigencia", "Unidad asig.", "Salario semanal", "Viajes/mes", "Estatus"].map(h => (
                                    <th key={h} className="text-left text-xs font-medium text-muted-foreground px-4 py-3 first:pl-5 last:pr-5 whitespace-nowrap">{h}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-border">
                            {filtered.map(d => {
                                const expired = isLicenseExpired(d.licencia_vigencia)
                                const soon = isLicenseSoon(d.licencia_vigencia)
                                return (
                                    <tr key={d.id} className="hover:bg-muted/30 transition-colors cursor-pointer">
                                        <td className="px-5 py-3.5">
                                            <div className="flex items-center gap-2.5">
                                                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-muted text-xs font-semibold text-muted-foreground">
                                                    {d.nombre.charAt(0)}{d.apellido.charAt(0)}
                                                </div>
                                                <div>
                                                    <div className="text-sm font-medium">{d.nombre} {d.apellido}</div>
                                                    <div className="text-xs text-muted-foreground">{d.telefono}</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-4 py-3.5">
                                            <div className="font-mono text-xs">{d.licencia_numero}</div>
                                            <div className="text-xs text-muted-foreground">Tipo {d.licencia_tipo}</div>
                                        </td>
                                        <td className="px-4 py-3.5">
                                            <div className={`flex items-center gap-1.5 text-xs ${expired ? "text-destructive" : soon ? "text-yellow-400" : "text-muted-foreground"}`}>
                                                {expired ? <AlertTriangle className="h-3 w-3" /> : soon ? <AlertTriangle className="h-3 w-3" /> : <CheckCircle className="h-3 w-3" />}
                                                {d.licencia_vigencia}
                                                {expired && <span className="font-medium">(vencida)</span>}
                                                {soon && !expired && <span className="font-medium">(próx. vencer)</span>}
                                            </div>
                                        </td>
                                        <td className="px-4 py-3.5 font-mono text-xs font-medium">{d.unidad_asignada ?? "—"}</td>
                                        <td className="px-4 py-3.5 text-xs tabular-nums">{MXN(d.salario_base)}</td>
                                        <td className="px-4 py-3.5 text-xs font-medium">{d.viajes_mes}</td>
                                        <td className="px-4 pr-5 py-3.5">
                                            <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium border ${statusBadge[d.estatus]}`}>
                                                {d.estatus.charAt(0) + d.estatus.slice(1).toLowerCase()}
                                            </span>
                                        </td>
                                    </tr>
                                )
                            })}
                        </tbody>
                    </table>
                </div>
            </Card>
        </div>
    )
}
