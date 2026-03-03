'use client'

import { useState, useEffect } from "react"
import { Search, Plus } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Sheet, SheetTrigger } from "@/components/ui/sheet"
import { PurchaseOrderForm } from "./purchase-order-form"

interface PurchaseOrder {
    id: number
    numero_orden: string
    proveedor: string
    fecha_orden: string
    fecha_entrega?: string
    total: number
    estatus: "PENDIENTE" | "RECIBIDA" | "CANCELADA"
    items: number
}

const MOCK_PURCHASES: PurchaseOrder[] = [
    { id: 1, numero_orden: "PO-2026-001", proveedor: "Llantera del Norte", fecha_orden: "2026-02-20", fecha_entrega: "2026-02-27", total: 54400, estatus: "RECIBIDA", items: 8 },
    { id: 2, numero_orden: "PO-2026-002", proveedor: "AutoZone Industrial", fecha_orden: "2026-02-25", fecha_entrega: "2026-03-04", total: 12800, estatus: "PENDIENTE", items: 15 },
    { id: 3, numero_orden: "PO-2026-003", proveedor: "Taller Hermanos García", fecha_orden: "2026-02-28", fecha_entrega: "2026-03-07", total: 28500, estatus: "PENDIENTE", items: 4 },
    { id: 4, numero_orden: "PO-2026-004", proveedor: "Pemex Transformación", fecha_orden: "2026-03-01", fecha_entrega: "2026-03-03", total: 76800, estatus: "RECIBIDA", items: 1 },
    { id: 5, numero_orden: "PO-2025-089", proveedor: "AutoZone Industrial", fecha_orden: "2025-12-10", total: 8900, estatus: "CANCELADA", items: 6 },
]

const statusBadge: Record<string, string> = {
    PENDIENTE: "bg-yellow-500/15 text-yellow-400 border-yellow-500/30",
    RECIBIDA: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    CANCELADA: "bg-muted text-muted-foreground border-border",
    pendiente: "bg-yellow-500/15 text-yellow-400 border-yellow-500/30",
    recibida: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    cancelada: "bg-muted text-muted-foreground border-border",
}

const MXN = (v: number) => new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN", maximumFractionDigits: 0 }).format(v)

export default function ComprasPage() {
    const [orders, setOrders] = useState<PurchaseOrder[]>(MOCK_PURCHASES)
    const [loading, setLoading] = useState(true)
    const [search, setSearch] = useState("")

    const fetchOrders = async () => {
        try {
            const res = await fetch("http://localhost:8001/api/v1/purchase-orders", {
                headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
            })
            const data = await res.json()
            if (Array.isArray(data?.items) && data.items.length > 0) {
                setOrders(data.items)
            } else {
                setOrders(MOCK_PURCHASES)
            }
        } catch (err) {
            console.error(err)
            setOrders(MOCK_PURCHASES)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchOrders()
    }, [])

    const filtered = orders.filter(p =>
        !search || [p.numero_orden, p.proveedor].some(f => f?.toLowerCase().includes(search.toLowerCase()))
    )

    const totalPendiente = orders.filter(p => p.estatus === "PENDIENTE").reduce((a, p) => a + (p.total || 0), 0)

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-xs text-muted-foreground uppercase tracking-widest font-medium">Compras</p>
                    <h1 className="text-2xl font-semibold tracking-tight mt-0.5">Órdenes de Compra</h1>
                </div>
                <Sheet onOpenChange={(open) => {
                    console.log("DEBUG: Compras Sheet onOpenChange:", open);
                    if (!open) fetchOrders();
                }}>
                    <SheetTrigger asChild>
                        <button
                            onClick={() => console.log("DEBUG: Nueva orden button clicked")}
                            className="flex items-center gap-2 rounded-md bg-foreground px-3.5 py-2 text-sm font-medium text-background hover:bg-foreground/90 transition-colors"
                        >
                            <Plus className="h-4 w-4" />
                            Nueva orden
                        </button>
                    </SheetTrigger>
                    <PurchaseOrderForm onSuccess={() => fetchOrders()} />
                </Sheet>
            </div>

            <div className="grid grid-cols-3 gap-3">
                <Card><CardContent className="pt-4 pb-4 px-4">
                    <div className="text-xl font-bold">{orders.filter(p => p.estatus === "PENDIENTE").length}</div>
                    <div className="text-xs text-muted-foreground mt-1">Órdenes pendientes</div>
                </CardContent></Card>
                <Card><CardContent className="pt-4 pb-4 px-4">
                    <div className="text-xl font-bold tabular-nums">{MXN(totalPendiente)}</div>
                    <div className="text-xs text-muted-foreground mt-1">Monto por recibir</div>
                </CardContent></Card>
                <Card><CardContent className="pt-4 pb-4 px-4">
                    <div className="text-xl font-bold">{orders.length}</div>
                    <div className="text-xs text-muted-foreground mt-1">Total órdenes</div>
                </CardContent></Card>
            </div>

            <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <input type="text" placeholder="Buscar por # orden, proveedor..." value={search} onChange={e => setSearch(e.target.value)}
                    className="w-full pl-9 pr-3 py-2 text-sm border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring" />
            </div>

            <Card>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-border">
                                {["# Orden", "Proveedor", "Fecha orden", "Fecha entrega", "Items", "Total", "Estatus"].map(h => (
                                    <th key={h} className="text-left text-xs font-medium text-muted-foreground px-4 py-3 first:pl-5 last:pr-5 whitespace-nowrap">{h}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-border">
                            {loading ? (
                                <tr><td colSpan={7} className="text-center py-8 text-muted-foreground">Cargando órdenes...</td></tr>
                            ) : filtered.length === 0 ? (
                                <tr><td colSpan={7} className="text-center py-8 text-muted-foreground">No se encontraron órdenes</td></tr>
                            ) : filtered.map(p => (
                                <tr key={p.id} className="hover:bg-muted/30 transition-colors cursor-pointer">
                                    <td className="px-5 py-3.5 font-mono text-xs font-medium">{p.numero_orden}</td>
                                    <td className="px-4 py-3.5 text-xs">{p.proveedor}</td>
                                    <td className="px-4 py-3.5 text-xs text-muted-foreground">{p.fecha_orden}</td>
                                    <td className="px-4 py-3.5 text-xs text-muted-foreground">{p.fecha_entrega ?? "—"}</td>
                                    <td className="px-4 py-3.5 text-xs text-muted-foreground">{p.items} artículos</td>
                                    <td className="px-4 py-3.5 text-xs font-medium tabular-nums">{MXN(p.total)}</td>
                                    <td className="px-4 pr-5 py-3.5">
                                        <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium border ${statusBadge[p.estatus] || statusBadge.PENDIENTE}`}>
                                            {(p.estatus || "PENDIENTE").charAt(0) + (p.estatus || "PENDIENTE").slice(1).toLowerCase()}
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
