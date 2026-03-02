"use client"

import { useState } from "react"
import { Search, Plus, Building2 } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"

interface Supplier {
    id: number
    nombre: string
    rfc: string
    tipo: string
    contacto_nombre: string
    telefono: string
    email: string
    estatus: "ACTIVO" | "INACTIVO"
    cxp_pendiente: number
}

const MOCK_SUPPLIERS: Supplier[] = [
    { id: 1, nombre: "Pemex Transformación Industrial", rfc: "PMI770901VT0", tipo: "COMBUSTIBLE", contacto_nombre: "Ing. Luis Herrera", telefono: "55-1111-2222", email: "lherrera@pemex.com", estatus: "ACTIVO", cxp_pendiente: 38400 },
    { id: 2, nombre: "Llantera del Norte, S.A.", rfc: "LNO890615GQ0", tipo: "REFACCIONES", contacto_nombre: "Sr. Marcos Rodríguez", telefono: "81-3333-4444", email: "mrodriguez@llanteranorte.com", estatus: "ACTIVO", cxp_pendiente: 52000 },
    { id: 3, nombre: "AutoZone Industrial, S.A. de C.V.", rfc: "AIN960420MZ0", tipo: "REFACCIONES", contacto_nombre: "Ing. Ana Martínez", telefono: "81-5555-6666", email: "amartinez@autozone.com.mx", estatus: "ACTIVO", cxp_pendiente: 0 },
    { id: 4, nombre: "Casetas CAPUFE", rfc: "CAP820101GQ0", tipo: "CASETAS", contacto_nombre: "Lic. Pedro Flores", telefono: "55-7777-8888", email: "pflores@capufe.gob.mx", estatus: "ACTIVO", cxp_pendiente: 0 },
    { id: 5, nombre: "Taller Hermanos García", rfc: "HGA991201AI0", tipo: "SERVICIOS", contacto_nombre: "C. Roberto García", telefono: "81-9999-0000", email: "contacto@tallergarcia.com", estatus: "ACTIVO", cxp_pendiente: 18500 },
    { id: 6, nombre: "Diesel Express del Norte", rfc: "DEN010315MZ0", tipo: "COMBUSTIBLE", contacto_nombre: "Ing. Claudia Soto", telefono: "81-1212-3434", email: "csoto@dieselexpress.mx", estatus: "ACTIVO", cxp_pendiente: 0 },
]

const tipoColor: Record<string, string> = {
    COMBUSTIBLE: "bg-orange-500/15 text-orange-400 border-orange-500/30",
    REFACCIONES: "bg-blue-500/15 text-blue-400 border-blue-500/30",
    SERVICIOS: "bg-violet-500/15 text-violet-400 border-violet-500/30",
    CASETAS: "bg-muted text-muted-foreground border-border",
    OTRO: "bg-muted text-muted-foreground border-border",
}

const MXN = (v: number) => new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN", maximumFractionDigits: 0 }).format(v)

export default function ProveedoresPage() {
    const [search, setSearch] = useState("")
    const filtered = MOCK_SUPPLIERS.filter(s =>
        !search || [s.nombre, s.rfc, s.tipo, s.contacto_nombre].some(f => f.toLowerCase().includes(search.toLowerCase()))
    )
    const totalCxP = MOCK_SUPPLIERS.filter(s => s.cxp_pendiente > 0).reduce((a, s) => a + s.cxp_pendiente, 0)

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-xs text-muted-foreground uppercase tracking-widest font-medium">Catálogos</p>
                    <h1 className="text-2xl font-semibold tracking-tight mt-0.5">Proveedores</h1>
                </div>
                <button className="flex items-center gap-2 rounded-md bg-foreground px-3.5 py-2 text-sm font-medium text-background hover:bg-foreground/90 transition-colors">
                    <Plus className="h-4 w-4" />
                    Nuevo proveedor
                </button>
            </div>

            <div className="grid grid-cols-3 gap-3">
                <Card><CardContent className="pt-4 pb-4 px-4">
                    <div className="text-xl font-bold">{MOCK_SUPPLIERS.filter(s => s.estatus === "ACTIVO").length}</div>
                    <div className="text-xs text-muted-foreground mt-1">Proveedores activos</div>
                </CardContent></Card>
                <Card><CardContent className="pt-4 pb-4 px-4">
                    <div className="text-xl font-bold tabular-nums">{MXN(totalCxP)}</div>
                    <div className="text-xs text-muted-foreground mt-1">CxP pendiente</div>
                </CardContent></Card>
                <Card><CardContent className="pt-4 pb-4 px-4">
                    <div className="text-xl font-bold">{MOCK_SUPPLIERS.length}</div>
                    <div className="text-xs text-muted-foreground mt-1">Total registrados</div>
                </CardContent></Card>
            </div>

            <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <input type="text" placeholder="Buscar por nombre, RFC, tipo..." value={search} onChange={e => setSearch(e.target.value)}
                    className="w-full pl-9 pr-3 py-2 text-sm border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring" />
            </div>

            <Card>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-border">
                                {["Proveedor", "RFC", "Tipo", "Contacto", "CxP Pendiente", "Estatus"].map(h => (
                                    <th key={h} className="text-left text-xs font-medium text-muted-foreground px-4 py-3 first:pl-5 last:pr-5 whitespace-nowrap">{h}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-border">
                            {filtered.map(s => (
                                <tr key={s.id} className="hover:bg-muted/30 transition-colors cursor-pointer">
                                    <td className="px-5 py-3.5">
                                        <div className="flex items-center gap-2.5">
                                            <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-muted">
                                                <Building2 className="h-3.5 w-3.5 text-muted-foreground" />
                                            </div>
                                            <div>
                                                <div className="text-sm font-medium">{s.nombre}</div>
                                                <div className="text-xs text-muted-foreground">{s.email}</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-4 py-3.5 font-mono text-xs text-muted-foreground">{s.rfc}</td>
                                    <td className="px-4 py-3.5">
                                        <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium border ${tipoColor[s.tipo]}`}>{s.tipo.charAt(0) + s.tipo.slice(1).toLowerCase()}</span>
                                    </td>
                                    <td className="px-4 py-3.5 text-xs text-muted-foreground">{s.contacto_nombre}</td>
                                    <td className="px-4 py-3.5 text-xs font-medium tabular-nums">
                                        {s.cxp_pendiente > 0 ? <span className="text-yellow-400">{MXN(s.cxp_pendiente)}</span> : <span className="text-muted-foreground">—</span>}
                                    </td>
                                    <td className="px-4 pr-5 py-3.5">
                                        <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium border ${s.estatus === "ACTIVO" ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/30" : "bg-muted text-muted-foreground border-border"}`}>{s.estatus.charAt(0) + s.estatus.slice(1).toLowerCase()}</span>
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
