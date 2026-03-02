"use client"

import { useState, useEffect } from "react"
import { Plus, Search, AlertTriangle, Clock, TrendingDown } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

type InvoiceStatus = "PENDIENTE" | "PARCIAL" | "PAGADA" | "VENCIDA" | "CANCELADA"
type InvoiceType = "POR_COBRAR" | "POR_PAGAR"

interface Invoice {
    id: number
    numero_factura: string
    tipo: InvoiceType
    estatus: InvoiceStatus
    cliente?: string
    proveedor?: string
    total: number
    monto_pagado: number
    fecha_vencimiento: string
    concepto: string
}

const MOCK_INVOICES: Invoice[] = [
    { id: 1, numero_factura: "FAC-2026-001", tipo: "POR_COBRAR", estatus: "VENCIDA", cliente: "Grupo Bimbo", total: 127500, monto_pagado: 0, fecha_vencimiento: "2026-02-15", concepto: "Servicio de transporte Alt→MTY" },
    { id: 2, numero_factura: "FAC-2026-002", tipo: "POR_COBRAR", estatus: "PARCIAL", cliente: "FEMSA Logística", total: 145600, monto_pagado: 72800, fecha_vencimiento: "2026-03-10", concepto: "Transporte Tam→CDMX" },
    { id: 3, numero_factura: "FAC-2026-003", tipo: "POR_COBRAR", estatus: "PENDIENTE", cliente: "Cemex", total: 78400, monto_pagado: 0, fecha_vencimiento: "2026-03-15", concepto: "Flete Saltillo→MTY" },
    { id: 4, numero_factura: "FAC-2026-004", tipo: "POR_COBRAR", estatus: "PAGADA", cliente: "Ternium", total: 110000, monto_pagado: 110000, fecha_vencimiento: "2026-02-28", concepto: "Transporte frontera" },
    { id: 5, numero_factura: "PO-2026-001", tipo: "POR_PAGAR", estatus: "VENCIDA", proveedor: "Pemex Diesel", total: 38400, monto_pagado: 0, fecha_vencimiento: "2026-02-20", concepto: "Diesel — Febrero 1era quincena" },
    { id: 6, numero_factura: "PO-2026-002", tipo: "POR_PAGAR", estatus: "PENDIENTE", proveedor: "Llantera del Norte", total: 52000, monto_pagado: 0, fecha_vencimiento: "2026-03-05", concepto: "Llantas 11R22.5 — ECO-003/ECO-007" },
    { id: 7, numero_factura: "PO-2026-003", tipo: "POR_PAGAR", estatus: "PARCIAL", proveedor: "Taller Hdos García", total: 18500, monto_pagado: 10000, fecha_vencimiento: "2026-03-01", concepto: "Reparación ECO-004 — motor" },
    { id: 8, numero_factura: "FAC-2026-005", tipo: "POR_COBRAR", estatus: "VENCIDA", cliente: "Liverpool", total: 89500, monto_pagado: 0, fecha_vencimiento: "2026-02-18", concepto: "Flete Alt→GDL" },
]

const statusBadge: Record<InvoiceStatus, string> = {
    PENDIENTE: "bg-yellow-500/15 text-yellow-400 border-yellow-500/30",
    PARCIAL: "bg-blue-500/15 text-blue-400 border-blue-500/30",
    PAGADA: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    VENCIDA: "bg-red-500/15 text-red-400 border-red-500/30",
    CANCELADA: "bg-muted text-muted-foreground border-border",
}

const MXN = (v: number) => new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN", maximumFractionDigits: 0 }).format(v)

function daysDiff(dateStr: string) {
    const diff = Math.ceil((new Date(dateStr).getTime() - Date.now()) / 86400000)
    return diff
}

export default function FinanzasPage() {
    const [invoices, setInvoices] = useState<Invoice[]>(MOCK_INVOICES)
    const [tab, setTab] = useState<"POR_COBRAR" | "POR_PAGAR">("POR_COBRAR")
    const [search, setSearch] = useState("")

    useEffect(() => {
        fetch(`http://localhost:8001/api/v1/invoices?tipo=${tab}`, {
            headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
        }).then(r => r.json()).then(data => {
            if (Array.isArray(data?.items)) setInvoices(data.items)
        }).catch(() => { })
    }, [tab])

    const displayed = invoices
        .filter(inv => inv.tipo === tab)
        .filter(inv => !search || [inv.numero_factura, inv.cliente ?? "", inv.proveedor ?? "", inv.concepto]
            .some(f => f.toLowerCase().includes(search.toLowerCase())))

    const totalPendiente = displayed.filter(i => i.estatus !== "PAGADA" && i.estatus !== "CANCELADA")
        .reduce((acc, i) => acc + (i.total - i.monto_pagado), 0)
    const totalVencido = displayed.filter(i => i.estatus === "VENCIDA")
        .reduce((acc, i) => acc + (i.total - i.monto_pagado), 0)
    const porVencer = displayed.filter(i => {
        const d = daysDiff(i.fecha_vencimiento)
        return d >= 0 && d <= 7 && i.estatus !== "PAGADA"
    }).length

    return (
        <div className="space-y-6">
            <div className="flex items-start justify-between">
                <div>
                    <p className="text-xs text-muted-foreground uppercase tracking-widest font-medium">Finanzas</p>
                    <h1 className="text-2xl font-semibold tracking-tight mt-0.5">Facturas</h1>
                </div>
                <button className="flex items-center gap-2 rounded-md bg-foreground px-3.5 py-2 text-sm font-medium text-background hover:bg-foreground/90 transition-colors">
                    <Plus className="h-4 w-4" />
                    Nueva factura
                </button>
            </div>

            {/* Tab toggle */}
            <div className="flex gap-1 rounded-lg border border-border bg-muted/30 p-1 w-fit">
                <button onClick={() => setTab("POR_COBRAR")} className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${tab === "POR_COBRAR" ? "bg-background shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground"}`}>
                    Cuentas por Cobrar
                </button>
                <button onClick={() => setTab("POR_PAGAR")} className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${tab === "POR_PAGAR" ? "bg-background shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground"}`}>
                    Cuentas por Pagar
                </button>
            </div>

            {/* Summary */}
            <div className="grid grid-cols-3 gap-3">
                <Card>
                    <CardContent className="pt-4 pb-4 px-4">
                        <div className="text-xl font-bold tabular-nums">{MXN(totalPendiente)}</div>
                        <div className="text-xs text-muted-foreground mt-1">Total pendiente</div>
                    </CardContent>
                </Card>
                <Card className="border-destructive/30">
                    <CardContent className="pt-4 pb-4 px-4">
                        <div className="flex items-center gap-2">
                            <AlertTriangle className="h-4 w-4 text-destructive" />
                            <div className="text-xl font-bold tabular-nums text-destructive">{MXN(totalVencido)}</div>
                        </div>
                        <div className="text-xs text-muted-foreground mt-1">Monto vencido</div>
                    </CardContent>
                </Card>
                <Card className="border-yellow-500/30">
                    <CardContent className="pt-4 pb-4 px-4">
                        <div className="flex items-center gap-2">
                            <Clock className="h-4 w-4 text-yellow-400" />
                            <div className="text-xl font-bold tabular-nums text-yellow-400">{porVencer}</div>
                        </div>
                        <div className="text-xs text-muted-foreground mt-1">Vencen esta semana</div>
                    </CardContent>
                </Card>
            </div>

            {/* Search */}
            <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <input
                    type="text"
                    placeholder="Buscar por # factura, cliente, proveedor, concepto..."
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                    className="w-full pl-9 pr-3 py-2 text-sm border border-input rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-ring"
                />
            </div>

            {/* Table */}
            <Card>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-border">
                                {["Factura", tab === "POR_COBRAR" ? "Cliente" : "Proveedor", "Concepto", "Total", "Pagado", "Saldo", "Vencimiento", "Estatus"].map(h => (
                                    <th key={h} className="text-left text-xs font-medium text-muted-foreground px-4 py-3 first:pl-5 last:pr-5 whitespace-nowrap">{h}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-border">
                            {displayed.map(inv => {
                                const days = daysDiff(inv.fecha_vencimiento)
                                const saldo = inv.total - inv.monto_pagado
                                return (
                                    <tr key={inv.id} className="hover:bg-muted/30 transition-colors">
                                        <td className="px-5 py-3.5 font-mono text-xs font-medium">{inv.numero_factura}</td>
                                        <td className="px-4 py-3.5 text-xs">{inv.cliente ?? inv.proveedor}</td>
                                        <td className="px-4 py-3.5 text-xs text-muted-foreground max-w-[200px] truncate">{inv.concepto}</td>
                                        <td className="px-4 py-3.5 text-xs font-medium tabular-nums">{MXN(inv.total)}</td>
                                        <td className="px-4 py-3.5 text-xs text-emerald-400 tabular-nums">{inv.monto_pagado > 0 ? MXN(inv.monto_pagado) : "—"}</td>
                                        <td className="px-4 py-3.5 text-xs font-medium tabular-nums">{saldo > 0 ? MXN(saldo) : <span className="text-emerald-400">Pagado</span>}</td>
                                        <td className="px-4 py-3.5">
                                            <div className={`text-xs flex items-center gap-1.5 ${days < 0 ? "text-destructive" : days <= 7 ? "text-yellow-400" : "text-muted-foreground"}`}>
                                                {days < 0 && <TrendingDown className="h-3 w-3" />}
                                                {inv.fecha_vencimiento}
                                                {days < 0 ? <span className="font-medium">({Math.abs(days)}d vencida)</span>
                                                    : days <= 7 && inv.estatus !== "PAGADA" ? <span className="font-medium">({days}d)</span>
                                                        : null}
                                            </div>
                                        </td>
                                        <td className="px-4 pr-5 py-3.5">
                                            <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border ${statusBadge[inv.estatus]}`}>
                                                {inv.estatus.charAt(0) + inv.estatus.slice(1).toLowerCase()}
                                            </span>
                                        </td>
                                    </tr>
                                )
                            })}
                            {displayed.length === 0 && (
                                <tr>
                                    <td colSpan={8} className="px-5 py-10 text-center text-sm text-muted-foreground">
                                        No se encontraron facturas
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
