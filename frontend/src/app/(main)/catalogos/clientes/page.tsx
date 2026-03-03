import { useState, useEffect } from "react"
import { Search, Plus, Building2, Phone, Mail, Trash2, Edit } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import Link from "next/link"

interface Client {
    id: number
    nombre: string
    rfc: string
    contacto_nombre: string
    telefono: string
    email: string
    dias_credito: number
    estatus: "ACTIVO" | "INACTIVO" | "SUSPENDIDO"
    cxc_pendiente?: number
}

const MXN = (v: number) => new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN", maximumFractionDigits: 0 }).format(v)

const statusBadge: Record<string, string> = {
    ACTIVO: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    INACTIVO: "bg-muted text-muted-foreground border-border",
    SUSPENDIDO: "bg-red-500/15 text-red-400 border-red-500/30",
}

export default function ClientesPage() {
    const [clients, setClients] = useState<Client[]>([])
    const [loading, setLoading] = useState(true)
    const [search, setSearch] = useState("")

    useEffect(() => {
        const fetchClients = async () => {
            try {
                const res = await fetch("http://localhost:8001/api/v1/clients", {
                    headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
                })
                const data = await res.json()
                if (data.items) setClients(data.items)
            } catch (err) {
                console.error(err)
            } finally {
                setLoading(false)
            }
        }
        fetchClients()
    }, [])

    const handleDelete = async (id: number) => {
        if (!confirm("¿Estás seguro de eliminar este cliente?")) return
        try {
            const res = await fetch(`http://localhost:8001/api/v1/clients/${id}`, {
                method: "DELETE",
                headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
            })
            if (res.ok) {
                setClients(clients.filter(c => c.id !== id))
            }
        } catch (err) {
            console.error(err)
        }
    }

    const filtered = clients.filter(c =>
        !search || [c.nombre, c.rfc, c.contacto_nombre, c.email].some(f => f?.toLowerCase().includes(search.toLowerCase()))
    )

    const totalCxC = clients.reduce((a, c) => a + (c.cxc_pendiente || 0), 0)

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-xs text-muted-foreground uppercase tracking-widest font-medium">Catálogos</p>
                    <h1 className="text-2xl font-semibold tracking-tight mt-0.5">Clientes</h1>
                </div>
                <Link href="/catalogos/clientes/nuevo" className="flex items-center gap-2 rounded-md bg-foreground px-3.5 py-2 text-sm font-medium text-background hover:bg-foreground/90 transition-colors">
                    <Plus className="h-4 w-4" />
                    Nuevo cliente
                </Link>
            </div>

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

            <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <input type="text" placeholder="Buscar por nombre, RFC, contacto..." value={search} onChange={e => setSearch(e.target.value)}
                    className="w-full pl-9 pr-3 py-2 text-sm border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring" />
            </div>

            <Card>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-border">
                                {["Empresa", "RFC", "Contacto", "Crédito", "CxC Pendiente", "Estatus", "Acciones"].map(h => (
                                    <th key={h} className="text-left text-xs font-medium text-muted-foreground px-4 py-3 first:pl-5 last:pr-5 whitespace-nowrap">{h}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-border">
                            {loading ? (
                                <tr><td colSpan={7} className="text-center py-8 text-muted-foreground">Cargando clientes...</td></tr>
                            ) : filtered.length === 0 ? (
                                <tr><td colSpan={7} className="text-center py-8 text-muted-foreground">No hay clientes registrados</td></tr>
                            ) : filtered.map(c => (
                                <tr key={c.id} className="hover:bg-muted/30 transition-colors group">
                                    <td className="px-5 py-3.5">
                                        <div className="flex items-center gap-2.5">
                                            <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-muted">
                                                <Building2 className="h-3.5 w-3.5 text-muted-foreground" />
                                            </div>
                                            <div>
                                                <div className="text-sm font-medium">{c.nombre}</div>
                                                <div className="flex items-center gap-3 mt-0.5">
                                                    {c.telefono && <span className="text-xs text-muted-foreground flex items-center gap-1"><Phone className="h-2.5 w-2.5" />{c.telefono}</span>}
                                                    {c.email && <span className="text-xs text-muted-foreground flex items-center gap-1"><Mail className="h-2.5 w-2.5" />{c.email}</span>}
                                                </div>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-4 py-3.5 font-mono text-xs text-muted-foreground">{c.rfc}</td>
                                    <td className="px-4 py-3.5 text-xs text-muted-foreground">{c.contacto_nombre}</td>
                                    <td className="px-4 py-3.5 text-xs">{c.dias_credito} días</td>
                                    <td className="px-4 py-3.5 text-xs font-medium tabular-nums">
                                        {(c.cxc_pendiente || 0) > 0 ? <span className="text-yellow-400">{MXN(c.cxc_pendiente || 0)}</span> : <span className="text-muted-foreground">—</span>}
                                    </td>
                                    <td className="px-4 py-3.5 text-xs">
                                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border ${statusBadge[c.estatus] || statusBadge.INACTIVO}`}>{c.estatus}</span>
                                    </td>
                                    <td className="px-4 pr-5 py-3.5">
                                        <div className="flex items-center gap-2">
                                            <button className="p-1 hover:bg-muted rounded transition-colors text-muted-foreground hover:text-foreground">
                                                <Edit className="h-4 w-4" />
                                            </button>
                                            <button onClick={() => handleDelete(c.id)} className="p-1 hover:bg-destructive/10 rounded transition-colors text-muted-foreground hover:text-destructive">
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
