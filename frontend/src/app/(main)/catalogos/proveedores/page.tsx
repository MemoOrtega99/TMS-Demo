"use client"

import { useState, useEffect } from "react"
import { Search, Plus, Building2, Trash2, Edit } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import Link from "next/link"

interface Supplier {
    id: number
    nombre: string
    rfc: string
    tipo: string
    contacto_nombre: string
    telefono: string
    email: string
    estatus: "ACTIVO" | "INACTIVO"
    cxp_pendiente?: number
}

const tipoColor: Record<string, string> = {
    COMBUSTIBLE: "bg-orange-500/15 text-orange-400 border-orange-500/30",
    REFACCIONES: "bg-blue-500/15 text-blue-400 border-blue-500/30",
    SERVICIOS: "bg-violet-500/15 text-violet-400 border-violet-500/30",
    CASETAS: "bg-muted text-muted-foreground border-border",
    OTRO: "bg-muted text-muted-foreground border-border",
}

const MXN = (v: number) => new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN", maximumFractionDigits: 0 }).format(v)

export default function ProveedoresPage() {
    const [suppliers, setSuppliers] = useState<Supplier[]>([])
    const [loading, setLoading] = useState(true)
    const [search, setSearch] = useState("")

    useEffect(() => {
        const fetchSuppliers = async () => {
            try {
                const res = await fetch("http://localhost:8001/api/v1/suppliers", {
                    headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
                })
                const data = await res.json()
                if (data.items) setSuppliers(data.items)
            } catch (err) {
                console.error(err)
            } finally {
                setLoading(false)
            }
        }
        fetchSuppliers()
    }, [])

    const handleDelete = async (id: number) => {
        if (!confirm("¿Estás seguro de eliminar este proveedor?")) return
        try {
            const res = await fetch(`http://localhost:8001/api/v1/suppliers/${id}`, {
                method: "DELETE",
                headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
            })
            if (res.ok) {
                setSuppliers(suppliers.filter(s => s.id !== id))
            }
        } catch (err) {
            console.error(err)
        }
    }

    const filtered = suppliers.filter(s =>
        !search || [s.nombre, s.rfc, s.tipo, s.contacto_nombre].some(f => f?.toLowerCase().includes(search.toLowerCase()))
    )

    const totalCxP = suppliers.reduce((a, s) => a + (s.cxp_pendiente || 0), 0)

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-xs text-muted-foreground uppercase tracking-widest font-medium">Catálogos</p>
                    <h1 className="text-2xl font-semibold tracking-tight mt-0.5">Proveedores</h1>
                </div>
                <Link href="/catalogos/proveedores/nuevo" className="flex items-center gap-2 rounded-md bg-foreground px-3.5 py-2 text-sm font-medium text-background hover:bg-foreground/90 transition-colors">
                    <Plus className="h-4 w-4" />
                    Nuevo proveedor
                </Link>
            </div>

            <div className="grid grid-cols-3 gap-3">
                <Card><CardContent className="pt-4 pb-4 px-4">
                    <div className="text-xl font-bold">{suppliers.filter(s => s.estatus === "ACTIVO").length}</div>
                    <div className="text-xs text-muted-foreground mt-1">Proveedores activos</div>
                </CardContent></Card>
                <Card><CardContent className="pt-4 pb-4 px-4">
                    <div className="text-xl font-bold tabular-nums">{MXN(totalCxP)}</div>
                    <div className="text-xs text-muted-foreground mt-1">CxP pendiente</div>
                </CardContent></Card>
                <Card><CardContent className="pt-4 pb-4 px-4">
                    <div className="text-xl font-bold">{suppliers.length}</div>
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
                                {["Proveedor", "RFC", "Tipo", "Contacto", "CxP Pendiente", "Estatus", "Acciones"].map(h => (
                                    <th key={h} className="text-left text-xs font-medium text-muted-foreground px-4 py-3 first:pl-5 last:pr-5 whitespace-nowrap">{h}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-border">
                            {loading ? (
                                <tr><td colSpan={7} className="text-center py-8 text-muted-foreground">Cargando proveedores...</td></tr>
                            ) : filtered.length === 0 ? (
                                <tr><td colSpan={7} className="text-center py-8 text-muted-foreground">No hay proveedores registrados</td></tr>
                            ) : filtered.map(s => (
                                <tr key={s.id} className="hover:bg-muted/30 transition-colors group">
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
                                        <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium border ${tipoColor[s.tipo] || tipoColor.OTRO}`}>{s.tipo}</span>
                                    </td>
                                    <td className="px-4 py-3.5 text-xs text-muted-foreground">{s.contacto_nombre}</td>
                                    <td className="px-4 py-3.5 text-xs font-medium tabular-nums">
                                        {(s.cxp_pendiente || 0) > 0 ? <span className="text-yellow-400">{MXN(s.cxp_pendiente || 0)}</span> : <span className="text-muted-foreground">—</span>}
                                    </td>
                                    <td className="px-4 py-3.5 text-xs">
                                        <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium border ${s.estatus === "ACTIVO" ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/30" : "bg-muted text-muted-foreground border-border"}`}>{s.estatus}</span>
                                    </td>
                                    <td className="px-4 pr-5 py-3.5">
                                        <div className="flex items-center gap-2">
                                            <button className="p-1 hover:bg-muted rounded transition-colors text-muted-foreground hover:text-foreground">
                                                <Edit className="h-4 w-4" />
                                            </button>
                                            <button onClick={() => handleDelete(s.id)} className="p-1 hover:bg-destructive/10 rounded transition-colors text-muted-foreground hover:text-destructive">
                                                <Trash2 className="h-4 w-4" />
                                            </button>
                                        </div>
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
