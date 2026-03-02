"use client"

import { useState } from "react"
import { Search, Plus, Building2, Phone, Mail } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"

interface Client {
    id: number
    nombre: string
    rfc: string
    contacto_nombre: string
    telefono: string
    email: string
    dias_credito: number
    estatus: "ACTIVO" | "INACTIVO" | "SUSPENDIDO"
    cxc_pendiente: number
}

const MOCK_CLIENTS: Client[] = [
    { id: 1, nombre: "Grupo Bimbo, S.A.B. de C.V.", rfc: "GBI050504GQ0", contacto_nombre: "Ing. Roberto Gómez", telefono: "55-1234-5678", email: "logistica@bimbo.com.mx", dias_credito: 30, estatus: "ACTIVO", cxc_pendiente: 127500 },
    { id: 2, nombre: "FEMSA Logística, S.A. de C.V.", rfc: "FLO870401MZ0", contacto_nombre: "Lic. Patricia Torres", telefono: "81-9876-5432", email: "ptorres@femsa.com", dias_credito: 45, estatus: "ACTIVO", cxc_pendiente: 72800 },
    { id: 3, nombre: "Cemex, S.A.B. de C.V.", rfc: "CEX880901AI0", contacto_nombre: "Ing. Carlos Ramírez", telefono: "81-2345-6789", email: "cramírez@cemex.com", dias_credito: 30, estatus: "ACTIVO", cxc_pendiente: 78400 },
    { id: 4, nombre: "Ternium México, S.A. de C.V.", rfc: "TEM961018KG0", contacto_nombre: "Dr. Alejandro Silva", telefono: "81-3456-7890", email: "asilva@ternium.com", dias_credito: 60, estatus: "ACTIVO", cxc_pendiente: 0 },
    { id: 5, nombre: "Liverpool, S.A.P.I. de C.V.", rfc: "LIV050602GQ0", contacto_nombre: "Lic. María Gutiérrez", telefono: "55-4567-8901", email: "mgutierrez@liverpool.com.mx", dias_credito: 30, estatus: "ACTIVO", cxc_pendiente: 89500 },
    { id: 6, nombre: "ArcelorMittal México, S.A.", rfc: "AME870515MZ0", contacto_nombre: "Ing. Fernando López", telefono: "55-5678-9012", email: "flopez@arcelormittal.com", dias_credito: 45, estatus: "ACTIVO", cxc_pendiente: 0 },
    { id: 7, nombre: "Peñoles, S.A.B. de C.V.", rfc: "PEN880420GQ0", contacto_nombre: "Lic. Diego Morales", telefono: "55-6789-0123", email: "dmorales@penoles.com.mx", dias_credito: 30, estatus: "INACTIVO", cxc_pendiente: 0 },
    { id: 8, nombre: "Whirlpool México, S.A. de C.V.", rfc: "WME960315AI0", contacto_nombre: "Sr. José Pérez", telefono: "55-7890-1234", email: "jperez@whirlpool.com", dias_credito: 45, estatus: "ACTIVO", cxc_pendiente: 0 },
]

const MXN = (v: number) => new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN", maximumFractionDigits: 0 }).format(v)

const statusBadge: Record<Client["estatus"], string> = {
    ACTIVO: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    INACTIVO: "bg-muted text-muted-foreground border-border",
    SUSPENDIDO: "bg-red-500/15 text-red-400 border-red-500/30",
}

export default function ClientesPage() {
    const [clients, setClients] = useState<Client[]>(MOCK_CLIENTS)
    const [search, setSearch] = useState("")

    const filtered = clients.filter(c =>
        !search || [c.nombre, c.rfc, c.contacto_nombre, c.email].some(f => f.toLowerCase().includes(search.toLowerCase()))
    )

    const totalCxC = clients.filter(c => c.cxc_pendiente > 0).reduce((a, c) => a + c.cxc_pendiente, 0)

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-xs text-muted-foreground uppercase tracking-widest font-medium">Catálogos</p>
                    <h1 className="text-2xl font-semibold tracking-tight mt-0.5">Clientes</h1>
                </div>
                <button className="flex items-center gap-2 rounded-md bg-foreground px-3.5 py-2 text-sm font-medium text-background hover:bg-foreground/90 transition-colors">
                    <Plus className="h-4 w-4" />
                    Nuevo cliente
                </button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-3">
                <Card><CardContent className="pt-4 pb-4 px-4">
                    <div className="text-xl font-bold">{clients.filter(c => c.estatus === "ACTIVO").length}</div>
                    <div className="text-xs text-muted-foreground mt-1">Clientes activos</div>
                </CardContent></Card>
                <Card><CardContent className="pt-4 pb-4 px-4">
                    <div className="text-xl font-bold tabular-nums">{MXN(totalCxC)}</div>
                    <div className="text-xs text-muted-foreground mt-1">CxC en proceso</div>
                </CardContent></Card>
                <Card><CardContent className="pt-4 pb-4 px-4">
                    <div className="text-xl font-bold">{clients.length}</div>
                    <div className="text-xs text-muted-foreground mt-1">Total registrados</div>
                </CardContent></Card>
            </div>

            {/* Search */}
            <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <input type="text" placeholder="Buscar por nombre, RFC, contacto..." value={search} onChange={e => setSearch(e.target.value)}
                    className="w-full pl-9 pr-3 py-2 text-sm border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring" />
            </div>

            {/* Table */}
            <Card>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-border">
                                {["Empresa", "RFC", "Contacto", "Crédito", "CxC Pendiente", "Estatus"].map(h => (
                                    <th key={h} className="text-left text-xs font-medium text-muted-foreground px-4 py-3 first:pl-5 last:pr-5 whitespace-nowrap">{h}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-border">
                            {filtered.map(c => (
                                <tr key={c.id} className="hover:bg-muted/30 transition-colors cursor-pointer group">
                                    <td className="px-5 py-3.5">
                                        <div className="flex items-center gap-2.5">
                                            <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-muted">
                                                <Building2 className="h-3.5 w-3.5 text-muted-foreground" />
                                            </div>
                                            <div>
                                                <div className="text-sm font-medium">{c.nombre}</div>
                                                <div className="flex items-center gap-3 mt-0.5">
                                                    <span className="text-xs text-muted-foreground flex items-center gap-1"><Phone className="h-2.5 w-2.5" />{c.telefono}</span>
                                                    <span className="text-xs text-muted-foreground flex items-center gap-1"><Mail className="h-2.5 w-2.5" />{c.email}</span>
                                                </div>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-4 py-3.5 font-mono text-xs text-muted-foreground">{c.rfc}</td>
                                    <td className="px-4 py-3.5 text-xs text-muted-foreground">{c.contacto_nombre}</td>
                                    <td className="px-4 py-3.5 text-xs">{c.dias_credito} días</td>
                                    <td className="px-4 py-3.5 text-xs font-medium tabular-nums">
                                        {c.cxc_pendiente > 0 ? <span className="text-yellow-400">{MXN(c.cxc_pendiente)}</span> : <span className="text-muted-foreground">—</span>}
                                    </td>
                                    <td className="px-4 pr-5 py-3.5">
                                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border ${statusBadge[c.estatus]}`}>{c.estatus.charAt(0) + c.estatus.slice(1).toLowerCase()}</span>
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
