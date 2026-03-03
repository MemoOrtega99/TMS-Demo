"use client"

import { useState, useEffect } from "react"
import { Search, Plus, UserCircle, Calendar, CheckCircle, AlertTriangle, Trash2, Edit } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import Link from "next/link"

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

const statusBadge: Record<string, string> = {
    ACTIVO: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    INACTIVO: "bg-muted text-muted-foreground border-border",
    VACACIONES: "bg-blue-500/15 text-blue-400 border-blue-500/30",
}

const MXN = (v: number) => new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN", maximumFractionDigits: 0 }).format(v)

function isLicenseExpired(dateStr: string) {
    if (!dateStr) return false
    return new Date(dateStr) < new Date()
}
function isLicenseSoon(dateStr: string) {
    if (!dateStr) return false
    const diff = (new Date(dateStr).getTime() - Date.now()) / 86400000
    return diff < 90 && diff >= 0
}

export default function OperadoresPage() {
    const [drivers, setDrivers] = useState<Driver[]>([])
    const [loading, setLoading] = useState(true)
    const [search, setSearch] = useState("")

    useEffect(() => {
        const fetchDrivers = async () => {
            try {
                const res = await fetch("http://localhost:8001/api/v1/drivers", {
                    headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
                })
                const data = await res.json()
                if (data.items) setDrivers(data.items)
            } catch (err) {
                console.error(err)
            } finally {
                setLoading(false)
            }
        }
        fetchDrivers()
    }, [])

    const handleDelete = async (id: number) => {
        if (!confirm("¿Estás seguro de eliminar este operador?")) return
        try {
            const res = await fetch(`http://localhost:8001/api/v1/drivers/${id}`, {
                method: "DELETE",
                headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
            })
            if (res.ok) {
                setDrivers(drivers.filter(d => d.id !== id))
            }
        } catch (err) {
            console.error(err)
        }
    }

    const filtered = drivers.filter(d =>
        !search || [d.nombre, d.apellido, d.licencia_numero, d.unidad_asignada ?? ""].some(f => f?.toLowerCase().includes(search.toLowerCase()))
    )

    const activos = drivers.filter(d => d.estatus === "ACTIVO").length
    const avgViajes = drivers.length > 0 ? (drivers.reduce((a, d) => a + (d.viajes_mes || 0), 0) / drivers.length).toFixed(1) : "0"

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-xs text-muted-foreground uppercase tracking-widest font-medium">Catálogos</p>
                    <h1 className="text-2xl font-semibold tracking-tight mt-0.5">Operadores</h1>
                </div>
                <Link href="/catalogos/operadores/nuevo" className="flex items-center gap-2 rounded-md bg-foreground px-3.5 py-2 text-sm font-medium text-background hover:bg-foreground/90 transition-colors">
                    <Plus className="h-4 w-4" />
                    Nuevo operador
                </Link>
            </div>

            <div className="grid grid-cols-3 gap-3">
                <Card><CardContent className="pt-4 pb-4 px-4">
                    <div className="text-xl font-bold">{activos}</div>
                    <div className="text-xs text-muted-foreground mt-1">Activos</div>
                </CardContent></Card>
                <Card><CardContent className="pt-4 pb-4 px-4">
                    <div className="text-xl font-bold">{avgViajes}</div>
                    <div className="text-xs text-muted-foreground mt-1">Viajes prom./mes</div>
                </CardContent></Card>
                <Card><CardContent className="pt-4 pb-4 px-4">
                    <div className="text-xl font-bold">{drivers.length}</div>
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
                                {["Operador", "Licencia", "Vigencia", "Unidad asig.", "Salario semanal", "Viajes/mes", "Estatus", "Acciones"].map(h => (
                                    <th key={h} className="text-left text-xs font-medium text-muted-foreground px-4 py-3 first:pl-5 last:pr-5 whitespace-nowrap">{h}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-border">
                            {loading ? (
                                <tr><td colSpan={8} className="text-center py-8 text-muted-foreground">Cargando operadores...</td></tr>
                            ) : filtered.length === 0 ? (
                                <tr><td colSpan={8} className="text-center py-8 text-muted-foreground">No hay operadores registrados</td></tr>
                            ) : filtered.map(d => {
                                const expired = d.licencia_vigencia ? isLicenseExpired(d.licencia_vigencia) : false
                                const soon = d.licencia_vigencia ? isLicenseSoon(d.licencia_vigencia) : false
                                return (
                                    <tr key={d.id} className="hover:bg-muted/30 transition-colors group">
                                        <td className="px-5 py-3.5">
                                            <div className="flex items-center gap-2.5">
                                                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-muted text-xs font-semibold text-muted-foreground">
                                                    {d.nombre?.charAt(0)}{d.apellido?.charAt(0)}
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
                                                {expired || soon ? <AlertTriangle className="h-3 w-3" /> : <CheckCircle className="h-3 w-3" />}
                                                {d.licencia_vigencia || "—"}
                                                {expired && <span className="font-medium">(vencida)</span>}
                                                {soon && !expired && <span className="font-medium">(próx. vencer)</span>}
                                            </div>
                                        </td>
                                        <td className="px-4 py-3.5 font-mono text-xs font-medium">{d.unidad_asignada ?? "—"}</td>
                                        <td className="px-4 py-3.5 text-xs tabular-nums">{MXN(d.salario_base || 0)}</td>
                                        <td className="px-4 py-3.5 text-xs font-medium">{d.viajes_mes}</td>
                                        <td className="px-4 py-3.5 text-xs">
                                            <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium border ${statusBadge[d.estatus] || statusBadge.INACTIVO}`}>
                                                {d.estatus}
                                            </span>
                                        </td>
                                        <td className="px-4 pr-5 py-3.5">
                                            <div className="flex items-center gap-2">
                                                <button className="p-1 hover:bg-muted rounded transition-colors text-muted-foreground hover:text-foreground">
                                                    <Edit className="h-4 w-4" />
                                                </button>
                                                <button onClick={() => handleDelete(d.id)} className="p-1 hover:bg-destructive/10 rounded transition-colors text-muted-foreground hover:text-destructive">
                                                    <Trash2 className="h-4 w-4" />
                                                </button>
                                            </div>
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
